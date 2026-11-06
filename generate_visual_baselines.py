import json
from pathlib import Path
from peabox_voice_studio.config import BASE_DIR,VISUAL_BASELINES_DIR
from peabox_voice_studio.services.visual_baselines import baseline_document,collect_screen_snapshots,screenshot_manifest,validate_baseline,write_baseline

def main():
 ui=(BASE_DIR/'peabox_voice_studio/ui.py').read_text(encoding='utf-8');screens=collect_screen_snapshots(BASE_DIR/'peabox_voice_studio/screens');document=baseline_document(ui,screens);issues=validate_baseline(document)
 if issues:raise SystemExit('Visual baseline validation failed: '+', '.join(issues))
 baseline=write_baseline(document);manifest=VISUAL_BASELINES_DIR/'screenshot_manifest.json';manifest.write_text(json.dumps(screenshot_manifest(document),ensure_ascii=False,indent=2));print(f'Wrote {baseline.name} and {manifest.name} with {len(screens)} screen snapshots.');return 0
if __name__=='__main__':raise SystemExit(main())
