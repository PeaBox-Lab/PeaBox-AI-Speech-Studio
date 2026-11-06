import streamlit as st
from peabox_voice_studio.config import DATABASE_PATH
from peabox_voice_studio.context import AppContext
from peabox_voice_studio.facades.governance import portfolio_governance
from peabox_voice_studio.services.object_storage import audit_manifest, copy_object, delete_object, list_objects, move_object, rebuild_manifest
from peabox_voice_studio.services.maintenance import apply_retention,complete,create,load,retention_preview,save,status
from peabox_voice_studio.services.recovery import backup_database,inventory,snapshot,validate_database
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
 tabs=st.tabs(['Portfolio','Recovery','Maintenance','Capacity','Objects'])
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
