import streamlit as st
from peabox_voice_studio.config import DATABASE_PATH
from peabox_voice_studio.context import AppContext
from peabox_voice_studio.facades.governance import portfolio_governance
from peabox_voice_studio.services.maintenance import apply_retention,complete,create,load,retention_preview,save,status
from peabox_voice_studio.services.recovery import backup_database,inventory,snapshot,validate_database
from peabox_voice_studio.ui import empty_state,kpi_card,section
def render(ctx:AppContext)->None:
 projects=ctx.store.list();rows=portfolio_governance(projects);files=inventory();plans=load();section('Portfolio operations','Portfolio governance, local recovery, maintenance evidence, and retention previews.')
 cols=st.columns(5)
 with cols[0]:kpi_card('Projects',str(len(projects)),'Local portfolio')
 with cols[1]:kpi_card('Open reviews',str(sum(x['open_comments'] for x in rows)),'Across projects')
 with cols[2]:kpi_card('Pending approvals',str(sum(x['pending_approvals'] for x in rows)),'Awaiting decisions')
 with cols[3]:kpi_card('Unassigned',str(sum(x['owner']=='Unassigned' for x in rows)),'Projects without owner')
 with cols[4]:kpi_card('Storage',f'{len(files)} files',f"{sum(x['bytes'] for x in files)/1048576:.1f} MB")
 tabs=st.tabs(['Portfolio','Recovery','Maintenance'])
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
