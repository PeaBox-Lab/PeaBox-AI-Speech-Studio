import json
from pathlib import Path
import streamlit as st
from peabox_voice_studio.config import DATABASE_PATH
from peabox_voice_studio.context import AppContext
from peabox_voice_studio.services.diagnostics import system_diagnostics
from peabox_voice_studio.services.files import safe_filename,user_safe_error
from peabox_voice_studio.services.health import apply_repairs,check_project,repair_preview
from peabox_voice_studio.services.recovery import backup_database,list_backups,list_quarantine,orphan_outputs,project_snapshot,quarantine_file,restore_database,restore_quarantine,storage_inventory,storage_summary,support_bundle,validate_database
from peabox_voice_studio.services.repository import health,list_projects,rebuild
from peabox_voice_studio.ui import empty_state,kpi_card,section

def render(ctx:AppContext)->None:
 projects=ctx.store.list();reports=[check_project(p) for p in projects];repo=health();inventory=storage_inventory();summary=storage_summary(inventory)
 section('Operations and recovery','Project health, repository integrity, storage review, reversible recovery, and sanitized support evidence.')
 cols=st.columns(4)
 with cols[0]:kpi_card('Repository','Ready' if repo['ready'] else 'Repair',f"{repo['projects']} indexed")
 with cols[1]:kpi_card('Projects',str(len(reports)),f"{sum(not x['healthy'] for x in reports)} need review")
 with cols[2]:kpi_card('Storage',f"{sum(x['files'] for x in summary.values())} files",f"{sum(x['bytes'] for x in summary.values())/1048576:.1f} MB")
 with cols[3]:kpi_card('Backups',str(len(list_backups())),'Local database recovery points')
 tabs=st.tabs(['Project health','Repository','Storage','Backups','Support'])
 with tabs[0]:
  if reports:st.dataframe([{'Project':next((p.name for p in projects if p.id==r['project_id']),r['project_id']),'Healthy':r['healthy'],'Errors':r['errors'],'Warnings':r['warnings']} for r in reports],use_container_width=True,hide_index=True)
  if not ctx.project:empty_state('No active project','Open a project to preview safe repairs.','Open Project Workspace','Projects')
  else:
   report=check_project(ctx.project)
   if report['issues']:st.dataframe(report['issues'],use_container_width=True,hide_index=True)
   else:st.success('Active project passed health checks.')
   actions=repair_preview(ctx.project,report)
   if actions:
    st.json(actions);confirm=st.checkbox('Apply previewed safe repairs')
    if st.button('Apply repair plan',disabled=not confirm):apply_repairs(ctx.project,actions);ctx.save_project(ctx.project);st.rerun()
   snapshot,manifest=project_snapshot(ctx.project);st.download_button('Download metadata snapshot',snapshot,f"{safe_filename(ctx.project.name)}_snapshot.zip",'application/zip');st.caption('Metadata snapshot only; external audio is not included.')
 with tabs[1]:
  if st.button('Rebuild project index'):rebuild([(p,ctx.store._path(p.id)) for p in projects]);st.rerun()
  st.json(health());rows=list_projects()
  if rows:st.dataframe(rows,use_container_width=True,hide_index=True)
 with tabs[2]:
  if summary:st.dataframe([{'Category':k,'Files':v['files'],'MB':round(v['bytes']/1048576,2)} for k,v in summary.items()],use_container_width=True,hide_index=True)
  orphans=orphan_outputs(projects);st.caption(f'{len(orphans)} unreferenced output file(s) detected. Quarantine is reversible.')
  if orphans:
   selected=st.selectbox('Unreferenced output',orphans,format_func=lambda p:f'{p.name} · {p.stat().st_size/1048576:.2f} MB');confirm=st.checkbox('Move selected file to quarantine')
   if st.button('Quarantine selected',disabled=not confirm):quarantine_file(selected);st.rerun()
  quarantine=list_quarantine()
  if quarantine:
   st.dataframe([{'Name':x['name'],'Reason':x['reason'],'Created':x['created_at'],'Restored':bool(x.get('restored_at'))} for x in quarantine],use_container_width=True,hide_index=True)
   restorable=[x for x in quarantine if not x.get('restored_at') and Path(x['quarantined']).exists()]
   if restorable:
    selected_q=st.selectbox('Restore quarantined file',restorable,format_func=lambda x:x['name']);restore_confirm=st.checkbox('Restore selected quarantined file')
    if st.button('Restore quarantined file',disabled=not restore_confirm):restore_quarantine(selected_q['id']);st.rerun()
 with tabs[3]:
  check=validate_database(DATABASE_PATH);st.write({'Current database valid':check['valid'],'Integrity':check['message']})
  if st.button('Create database backup'):path=backup_database();st.success(f'Created {path.name}');st.rerun()
  backups=list_backups()
  if backups:
   st.dataframe([{'Backup':p.name,'MB':round(p.stat().st_size/1048576,3),'Valid':validate_database(p)['valid']} for p in backups],use_container_width=True,hide_index=True)
   selected_b=st.selectbox('Backup to restore',backups,format_func=lambda p:p.name);restore_db_confirm=st.checkbox('Replace current index from selected backup')
   if st.button('Restore database backup',disabled=not restore_db_confirm):
    try:restore_database(selected_b);st.success('Database restored; a rollback backup was retained.');st.rerun()
    except Exception as exc:st.error('Restore failed: '+user_safe_error(exc))
 with tabs[4]:
  st.info('Support bundles exclude credentials, project text, transcripts, media content, and absolute user paths.')
  bundle,report=support_bundle(system_diagnostics(),health(),inventory)
  st.download_button('Download sanitized support bundle',bundle,'peabox_support_bundle.zip','application/zip')
  st.json({'Version':report['version'],'Storage':report['storage_summary'],'Exclusions':report['exclusions']})
