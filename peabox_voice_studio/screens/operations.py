import streamlit as st
from peabox_voice_studio.context import AppContext
from peabox_voice_studio.services.health import apply_repairs,check_project,repair_preview
from peabox_voice_studio.services.repository import health,list_projects,rebuild
from peabox_voice_studio.ui import empty_state,kpi_card,section
def render(ctx:AppContext)->None:
 projects=ctx.store.list();reports=[check_project(p) for p in projects];repo=health();section('Operational health','Project health, safe repairs, and rebuildable repository status.')
 cols=st.columns(3)
 with cols[0]:kpi_card('Repository','Ready' if repo['ready'] else 'Repair',f"{repo['projects']} indexed")
 with cols[1]:kpi_card('Projects',str(len(reports)),f"{sum(not x['healthy'] for x in reports)} need review")
 with cols[2]:kpi_card('Errors',str(sum(x['errors'] for x in reports)),'Across all projects')
 tabs=st.tabs(['Project health','Repository'])
 with tabs[0]:
  if not ctx.project:empty_state('No active project','Open a project to preview repairs.','Open Project Workspace','Projects')
  else:
   report=check_project(ctx.project)
   if report['issues']:st.dataframe(report['issues'],use_container_width=True,hide_index=True)
   else:st.success('Active project passed health checks.')
   actions=repair_preview(ctx.project,report);confirm=st.checkbox('Apply previewed safe repairs') if actions else False
   if actions and st.button('Apply repair plan',disabled=not confirm):apply_repairs(ctx.project,actions);ctx.save_project(ctx.project);st.rerun()
 with tabs[1]:
  if st.button('Rebuild project index'):rebuild([(p,ctx.store._path(p.id)) for p in projects]);st.rerun()
  rows=list_projects()
  if rows:st.dataframe(rows,use_container_width=True,hide_index=True)
