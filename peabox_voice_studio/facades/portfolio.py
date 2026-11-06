from peabox_voice_studio.services.bundles import export_timeline_bundle,import_timeline_bundle
from peabox_voice_studio.services.preferences import mark_project_opened,resolve_projects,save_preferences,toggle_favorite
from peabox_voice_studio.services.projects import ProjectStore,export_project,split_script_into_blocks
__all__=['ProjectStore','export_project','export_timeline_bundle','import_timeline_bundle','mark_project_opened','resolve_projects','save_preferences','split_script_into_blocks','toggle_favorite']
def project_access_rows(projects,preferences):
 favorites=resolve_projects(projects,preferences.get('favorite_project_ids',[]));recent=resolve_projects(projects,preferences.get('recent_project_ids',[]));favorite_ids={p.id for p in favorites};ordered=favorites+[p for p in recent if p.id not in favorite_ids]
 return [{'id':p.id,'name':p.name,'updated_at':p.updated_at,'favorite':p.id in favorite_ids} for p in ordered]
def portfolio_summary(projects):
 return {'projects':len(projects),'blocks':sum(len(p.blocks) for p in projects),'characters':sum(len(p.script) for p in projects),'renders':sum(len(p.render_history) for p in projects)}
__all__ += ['portfolio_summary','project_access_rows']
