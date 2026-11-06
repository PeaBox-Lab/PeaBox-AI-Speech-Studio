import streamlit as st
from peabox_voice_studio.config import DATABASE_PATH
from peabox_voice_studio.context import AppContext
from peabox_voice_studio.facades.governance import portfolio_governance
from peabox_voice_studio.services.object_storage import audit_manifest, copy_object, delete_object, list_objects, move_object, rebuild_manifest
from peabox_voice_studio.services.maintenance import apply_retention,complete,create,load,retention_preview,save,status
from peabox_voice_studio.services.recovery import backup_database,inventory,snapshot,validate_database
from peabox_voice_studio.services.backend_resilience import CircuitBreaker, ResilientBackend, RetryPolicy, resilience_report
from peabox_voice_studio.services.resilience_profiles import active_profile, audit_log as resilience_audit, clone_profile, create_profile, delete_draft, instantiate, list_profiles, profile_diff, transition, update_profile
from peabox_voice_studio.services.visual_baselines import baseline_document, collect_screen_snapshots, screenshot_manifest, validate_baseline
from peabox_voice_studio.services.storage_backends import MemoryBackend, contract_report, migration_preview as backend_migration_preview, migrate as migrate_backend, registry as backend_registry
from peabox_voice_studio.services.storage_policy import active_reservations,load_policy,policy_status,release_reservation,reserve,save_policy
from peabox_voice_studio.ui import empty_state,kpi_card,section
def render(ctx:AppContext)->None:
 projects=ctx.store.list();rows=portfolio_governance(projects);files=inventory();plans=load();section('Portfolio operations','Portfolio governance, local recovery, maintenance evidence, and retention previews.')
 cols=st.columns(5)
 with cols[0]:kpi_card('Projects',str(len(projects)),'Local portfolio')
 with cols[1]:kpi_card('Open reviews',str(sum(x['open_comments'] for x in rows)),'Across projects')
 with cols[2]:kpi_card('Pending approvals',str(sum(x['pending_approvals'] for x in rows)),'Awaiting decisions')
 with cols[3]:kpi_card('Unassigned',str(sum(x['owner']=='Unassigned' for x in rows)),'Projects without owner')
 with cols[4]:kpi_card('Storage',f'{len(files)} files',f"{sum(x['bytes'] for x in files)/1048576:.1f} MB")
 tabs=st.tabs(['Portfolio','Recovery','Maintenance','Capacity','Objects','Backends','Resilience','Profiles','Visual QA'])
 with tabs[0]:
  if rows:st.dataframe(rows,use_container_width=True,hide_index=True)
  else:empty_state('No projects','Create a project to begin portfolio monitoring.','Open Project Workspace','Projects')
 with tabs[1]:
  st.write({'Database valid':validate_database(DATABASE_PATH)})
  if st.button('Create database backup'):st.success(f'Created {backup_database().name}')
  if ctx.project:st.download_button('Download metadata snapshot',snapshot(ctx.project),f'{ctx.project.name}_snapshot.zip','application/zip');st.caption('Metadata only; external audio is excluded.')
 with tabs[2]:
  st.caption('Plans are evaluated when this screen opens; no background scheduler runs.')
  name=st.text_input('Plan name',value='Weekly operations review');frequency=st.selectbox('Frequency',['Daily','Weekly','Monthly','Quarterly'],index=1)
  if st.button('Create maintenance plan'):plans.append(create(name,frequency));save(plans);st.rerun()
  if plans:
   plan=st.selectbox('Plan',plans,format_func=lambda x:f"{x['name']} · {status(x)}");notes=st.text_area('Completion notes')
   if st.button('Complete plan'):complete(plan,notes);save(plans);st.rerun()
  preview=retention_preview();st.write({'Retention candidates':preview['files'],'Bytes':preview['bytes']})
  if preview['candidates']:st.dataframe(preview['candidates'],use_container_width=True,hide_index=True)
  confirm=st.checkbox('Permanently remove every file in this preview',disabled=not preview['candidates'])
  if st.button('Apply retention preview',disabled=not confirm):apply_retention(preview);st.rerun()
 with tabs[3]:
  _render_capacity_tab()
 with tabs[4]:
  _render_object_storage_tab()
 with tabs[5]:
  _render_storage_backends_tab()
 with tabs[6]:
  _render_backend_resilience_tab()
 with tabs[7]:
  _render_resilience_profiles_tab()
 with tabs[8]:
  _render_visual_qa_tab()

# Capacity policy is rendered as the fourth Operations tab.
def _render_capacity_tab():
 policy=load_policy();st.caption('Quotas apply to generated outputs, downloaded models, recovery artifacts, and worker state. Project JSON is excluded.')
 enabled=st.checkbox('Enable local storage quotas',value=policy['enabled']);warning=st.slider('Warning threshold percent',50,95,int(policy['warning_percent']))
 labels={'outputs':'Generated outputs','models':'Downloaded models','recovery':'Backups and recovery','worker':'Worker queue and events'};values={}
 cols=st.columns(4)
 for i,(key,label) in enumerate(labels.items()):values[key]=int(cols[i].number_input(label+' limit (MB)',min_value=1,max_value=102400,value=max(1,int(policy['categories'][key]/1048576))))*1048576
 if st.button('Save storage policy'):save_policy({'enabled':enabled,'warning_percent':warning,'categories':values});st.rerun()
 states=policy_status();st.dataframe([{'Category':x['category'],'Used MB':round(x['used']/1048576,2),'Reserved MB':round(x['reserved']/1048576,2),'Limit MB':round(x['limit']/1048576,2),'Percent':x['percent'],'Warning':x['warning'],'Blocked':x['blocked']} for x in states],use_container_width=True,hide_index=True)
 reservations=active_reservations()
 if reservations:
  selected=st.selectbox('Active reservation',reservations,format_func=lambda x:f"{x['category']} · {x['bytes']/1048576:.2f} MB · {x['purpose']}")
  if st.button('Release selected reservation'):release_reservation(selected['id']);st.rerun()
 category=st.selectbox('Test reservation category',list(labels));amount=st.number_input('Reservation size (MB)',min_value=1,max_value=10240,value=10);purpose=st.text_input('Reservation purpose',value='Planned local operation')
 if st.button('Create capacity reservation'):
  try:reserve(category,int(amount)*1048576,purpose);st.success('Capacity reserved. Release it when the planned operation is cancelled or complete.');st.rerun()
  except OSError as exc:st.error(str(exc))

def _render_object_storage_tab():
 st.caption('Logical object keys map to the existing local managed directories. No remote storage is configured in this release.')
 o1,o2=st.columns(2)
 if o1.button('Rebuild object manifest'):rebuild_manifest();st.rerun()
 audit=audit_manifest()
 if o2.button('Audit object manifest'):st.session_state['object_audit']=audit
 st.write({'Registered objects':audit['objects'],'Healthy':audit['healthy'],'Issues':len(audit['issues'])})
 if audit['issues']:st.dataframe(audit['issues'],use_container_width=True,hide_index=True)
 objects=list_objects()
 if objects:
  namespace=st.selectbox('Object namespace',['All','outputs','models','backups','quarantine','support','worker'])
  visible=objects if namespace=='All' else [x for x in objects if x['namespace']==namespace]
  st.dataframe(visible,use_container_width=True,hide_index=True)
  selected=st.selectbox('Selected object',visible,format_func=lambda x:f"{x['namespace']}:{x['key']} · {x['bytes']/1048576:.2f} MB") if visible else None
  if selected:
   target_namespace=st.selectbox('Target namespace',['outputs','models','backups','quarantine','support','worker'],index=['outputs','models','backups','quarantine','support','worker'].index(selected['namespace']))
   target_key=st.text_input('Target object key',value=selected['key'])
   c1,c2,c3=st.columns(3)
   if c1.button('Copy object'):
    try:copy_object(selected['namespace'],selected['key'],target_namespace,target_key);st.rerun()
    except Exception as exc:st.error(str(exc))
   move_confirm=st.checkbox('Move removes the source after verified copy')
   if c2.button('Move object',disabled=not move_confirm):
    try:move_object(selected['namespace'],selected['key'],target_namespace,target_key);st.rerun()
    except Exception as exc:st.error(str(exc))
   delete_confirm=st.checkbox('Permanently delete selected object')
   if c3.button('Delete object',disabled=not delete_confirm):
    try:delete_object(selected['namespace'],selected['key']);st.rerun()
    except Exception as exc:st.error(str(exc))
 else:st.info('Rebuild the manifest to register existing managed files.')

def _render_storage_backends_tab():
 st.caption('Local is the active durable backend. Memory is a non-persistent validation backend for contract and migration testing.')
 local=backend_registry.create('local');memory=MemoryBackend();st.write({'Registered backends':backend_registry.names(),'Local contract':contract_report(local),'Memory contract':contract_report(memory)})
 local_objects=local.list();st.write({'Local objects':len(local_objects),'Local audit healthy':local.audit()['healthy']})
 namespace=st.selectbox('Migration namespace',['All','outputs','models','backups','quarantine','support','worker'],key='backend_namespace')
 preview=backend_migration_preview(local,memory,None if namespace=='All' else namespace);st.write({'Preview files':preview['files'],'Preview MB':round(preview['bytes']/1048576,3),'Source':preview['source'],'Target':preview['target']})
 if preview['items']:st.dataframe(preview['items'],use_container_width=True,hide_index=True)
 confirm=st.checkbox('Run non-persistent migration test into memory backend',disabled=not preview['items'])
 if st.button('Validate backend migration',disabled=not confirm):
  result=migrate_backend(preview,local,memory);st.write({'Migrated':result['files'],'Failed':len(result['failed']),'Memory audit healthy':memory.audit()['healthy']})
 st.info('Backend selection is not persisted. Remote backends require a future explicit credential and approval workflow.')

def _render_backend_resilience_tab():
 st.caption('Resilience controls wrap a backend at runtime. They do not change stored objects or persist remote credentials.')
 attempts=st.slider('Retry attempts',1,5,3);delay=st.number_input('Initial retry delay seconds',min_value=0.0,max_value=10.0,value=0.05,step=0.05);timeout=st.number_input('Operation timeout seconds',min_value=0.1,max_value=60.0,value=5.0,step=0.5);threshold=st.slider('Circuit failure threshold',1,10,3);cooldown=st.number_input('Circuit recovery seconds',min_value=1,max_value=3600,value=30)
 local=ResilientBackend(backend_registry.create('local'),RetryPolicy(attempts,delay,2.0),CircuitBreaker(threshold,cooldown),timeout);memory=ResilientBackend(MemoryBackend(),RetryPolicy(attempts,delay,2.0),CircuitBreaker(threshold,cooldown),timeout)
 if st.button('Run backend health probes'):
  st.session_state['backend_resilience_report']=resilience_report([local,memory])
 report=st.session_state.get('backend_resilience_report')
 if report:st.dataframe([{'Backend':x['backend'],'Healthy':x['healthy'],'Circuit':x.get('circuit',{}).get('state','n/a'),'Calls':x.get('metrics',{}).get('calls',0),'Retries':x.get('metrics',{}).get('retries',0),'Timeouts':x.get('metrics',{}).get('timeouts',0),'Last error':x.get('metrics',{}).get('last_error','')} for x in report],use_container_width=True,hide_index=True)
 st.info('The local backend is fast and durable. These policies establish the contract required before any future remote backend is approved.')

def _render_resilience_profiles_tab():
 st.caption('Profiles persist resilience settings without credentials. Activation requires an approved profile and uses local actor labels, not authenticated identities.')
 actor=st.text_input('Profile actor label',value=st.session_state.get('resilience_actor','Local User'));st.session_state['resilience_actor']=actor
 profiles=list_profiles();name=st.text_input('New profile name',value='Local backend standard');backend=st.selectbox('Profile backend',['local','memory']);description=st.text_area('Profile description',height=70)
 c1,c2,c3=st.columns(3);attempts=c1.number_input('Profile retry attempts',1,10,3);timeout=c2.number_input('Profile timeout seconds',0.1,3600.0,5.0);threshold=c3.number_input('Profile circuit threshold',1,100,3)
 d1,d2,d3=st.columns(3);delay=d1.number_input('Profile retry delay',0.0,60.0,0.05);backoff=d2.number_input('Profile backoff',1.0,10.0,2.0);recovery=d3.number_input('Profile recovery seconds',1,86400,30)
 settings={'attempts':attempts,'delay_seconds':delay,'backoff':backoff,'timeout_seconds':timeout,'failure_threshold':threshold,'recovery_seconds':recovery}
 if st.button('Create Draft resilience profile'):
  try:create_profile(name,backend,settings,actor,description);st.rerun()
  except Exception as exc:st.error(str(exc))
 if profiles:
  selected=st.selectbox('Saved resilience profile',profiles,format_func=lambda x:f"{x['name']} · {x['backend']} · {x['status']}")
  st.json({'Status':selected['status'],'Backend':selected['backend'],'Creator':selected['created_by'],'Reviewer':selected.get('reviewer') or 'None','Settings':selected['settings']})
  note=st.text_input('Review or transition note');actions=st.columns(6)
  transitions={'Draft':'In Review','In Review':'Approved','Changes Requested':'In Review','Approved':'Active','Active':'Approved','Archived':'Draft'}
  target=transitions.get(selected['status'])
  if actions[0].button('Advance profile',disabled=not target):
   try:transition(selected['id'],target,actor,note);st.rerun()
   except Exception as exc:st.error(str(exc))
  if actions[1].button('Request changes',disabled=selected['status']!='In Review'):
   try:transition(selected['id'],'Changes Requested',actor,note);st.rerun()
   except Exception as exc:st.error(str(exc))
  if actions[2].button('Archive profile',disabled=selected['status']=='Archived'):
   try:transition(selected['id'],'Archived',actor,note);st.rerun()
   except Exception as exc:st.error(str(exc))
  if actions[3].button('Clone profile'):
   try:clone_profile(selected['id'],f"{selected['name']} copy",actor);st.rerun()
   except Exception as exc:st.error(str(exc))
  if actions[4].button('Delete Draft',disabled=selected['status']!='Draft'):
   try:delete_draft(selected['id'],actor);st.rerun()
   except Exception as exc:st.error(str(exc))
  active=active_profile(selected['backend'])
  if actions[5].button('Probe Active profile',disabled=not active):
   try:
    wrapped=instantiate(active,backend_registry.create(active['backend']));st.session_state['active_profile_probe']=wrapped.health()
   except Exception as exc:st.error(str(exc))
  if active and active['id']!=selected['id']:st.dataframe(profile_diff(selected,active),use_container_width=True,hide_index=True)
  if st.session_state.get('active_profile_probe'):st.json(st.session_state['active_profile_probe'])
 audit=resilience_audit()
 if audit:
  with st.expander('Resilience profile audit history'):st.dataframe(list(reversed(audit[-100:])),use_container_width=True,hide_index=True)

def _render_visual_qa_tab():
 from peabox_voice_studio.config import BASE_DIR
 ui_source=(BASE_DIR/'peabox_voice_studio/ui.py').read_text(encoding='utf-8');screens=collect_screen_snapshots(BASE_DIR/'peabox_voice_studio/screens');document=baseline_document(ui_source,screens);issues=validate_baseline(document);manifest=screenshot_manifest(document)
 st.caption('Deterministic source snapshots validate navigation, theme, labels, widget calls, responsive rules, and contrast. PNG capture remains an external browser step.')
 cols=st.columns(4);cols[0].metric('Pages',sum(len(x['pages']) for x in document['navigation']['groups']));cols[1].metric('Screen modules',len(screens));cols[2].metric('Planned captures',len(manifest['captures']));cols[3].metric('Contract issues',len(issues))
 st.write({'Baseline hash':document['hash'],'Sidebar contrast':document['contrast']['sidebar_text_on_control'],'Card contrast':document['contrast']['ink_on_card'],'Viewports':[x['name'] for x in manifest['viewports']]})
 if issues:st.error('Visual contract issues: '+', '.join(issues))
 else:st.success('Deterministic visual contracts passed.')
 st.download_button('Download UI baseline JSON',json.dumps(document,ensure_ascii=False,indent=2),f"ui_baseline_{document['version']}.json",'application/json')
 st.download_button('Download screenshot manifest',json.dumps(manifest,ensure_ascii=False,indent=2),'screenshot_manifest.json','application/json')
