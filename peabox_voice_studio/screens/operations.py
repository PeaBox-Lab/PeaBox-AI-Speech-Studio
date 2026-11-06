import json
import streamlit as st
from peabox_voice_studio.context import AppContext
from peabox_voice_studio.services.health import apply_repairs,check_project,repair_preview
from peabox_voice_studio.services.maintenance_plans import complete,create,load,save,status
from peabox_voice_studio.services.operations import read,record
from peabox_voice_studio.services.repository import health,list_projects,rebuild
from peabox_voice_studio.ui import empty_state,kpi_card,section

def render(ctx: AppContext) -> None:
    projects=ctx.store.list();reports=[check_project(p) for p in projects];repo=health();plans=load();project=ctx.project
    section("Operational health","Project health, safe repairs, repository index, and maintenance evidence.")
    cols=st.columns(4)
    with cols[0]:kpi_card("Repository","Ready" if repo['ready'] else "Repair",f"{repo['projects']} indexed")
    with cols[1]:kpi_card("Projects",str(len(reports)),f"{sum(not r['healthy'] for r in reports)} need repair")
    with cols[2]:kpi_card("Errors",str(sum(r['errors'] for r in reports)),"Across all projects")
    with cols[3]:kpi_card("Plans",str(len(plans)),f"{sum(status(x)=='Overdue' for x in plans)} overdue")
    tabs=st.tabs(["Project health","Repository","Maintenance plans","Events"])
    with tabs[0]:
        if reports:st.dataframe([{"Project":next((p.name for p in projects if p.id==r['project_id']),r['project_id']),"Healthy":r['healthy'],"Errors":r['errors'],"Warnings":r['warnings']} for r in reports],use_container_width=True,hide_index=True)
        if not project:empty_state("No active project","Open a project to preview repairs.","Open Project Workspace","Projects")
        else:
            report=check_project(project)
            if report['issues']:st.dataframe(report['issues'],use_container_width=True,hide_index=True)
            else:st.success("Active project passed health checks.")
            actions=repair_preview(project,report)
            if actions:
                st.dataframe(actions,use_container_width=True,hide_index=True);confirm=st.checkbox("Apply all previewed safe repairs")
                if st.button("Apply repair plan",disabled=not confirm):
                    applied=apply_repairs(project,actions);ctx.save_project(project);record("health.repairs_applied",project_id=project.id,details={"actions":applied});st.rerun()
    with tabs[1]:
        if st.button("Rebuild project index"):
            rebuild([(p,ctx.store._path(p.id),next((r['errors']+r['warnings'] for r in reports if r['project_id']==p.id),0)) for p in projects]);st.rerun()
        st.json(health());st.dataframe(list_projects(),use_container_width=True,hide_index=True)
    with tabs[2]:
        name=st.text_input("Plan name",value="Weekly health review");freq=st.selectbox("Frequency",["Daily","Weekly","Monthly","Quarterly"])
        if st.button("Create maintenance plan"):plans.append(create(name,freq));save(plans);st.rerun()
        if plans:
            selected=st.selectbox("Plans",plans,format_func=lambda x:f"{x['name']} · {status(x)}")
            st.dataframe([{"Task":x,"Complete":False} for x in selected['tasks']],use_container_width=True,hide_index=True);notes=st.text_area("Completion notes")
            if st.button("Complete plan"):complete(selected,{x:"Complete" for x in selected['tasks']},notes);save(plans);st.rerun()
    with tabs[3]:
        events=read(500)
        if events:st.dataframe(events,use_container_width=True,hide_index=True)
        else:st.info("No operational events.")
