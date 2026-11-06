import argparse,json
from pathlib import Path
from peabox_voice_studio.config import VISUAL_BASELINES_DIR,VISUAL_CAPTURE_BASELINE_DIR,VISUAL_CAPTURE_CANDIDATE_DIR,VISUAL_DIFF_DIR,VISUAL_REPORT_PATH
from peabox_voice_studio.services.visual_pixels import capture_inventory,compare_capture_set,write_report
def main():
 p=argparse.ArgumentParser(description='Compare PeaBox PNG capture sets');p.add_argument('--baseline',default=str(VISUAL_CAPTURE_BASELINE_DIR));p.add_argument('--candidate',default=str(VISUAL_CAPTURE_CANDIDATE_DIR));p.add_argument('--manifest',default=str(VISUAL_BASELINES_DIR/'screenshot_manifest.json'));p.add_argument('--diff-dir',default=str(VISUAL_DIFF_DIR));p.add_argument('--report',default=str(VISUAL_REPORT_PATH));p.add_argument('--pixel-threshold',type=int,default=0);p.add_argument('--allowed-changed-percent',type=float,default=0);args=p.parse_args();manifest=json.loads(Path(args.manifest).read_text());base=capture_inventory(args.baseline,manifest);candidate=capture_inventory(args.candidate,manifest)
 if not base['ready'] or not candidate['ready']:
  report={'schema':1,'success':False,'reason':'capture_set_not_ready','baseline':{k:v for k,v in base.items() if k!='rows'},'candidate':{k:v for k,v in candidate.items() if k!='rows'}};write_report(report,args.report);print(json.dumps(report,indent=2));return 2
 report=compare_capture_set(args.baseline,args.candidate,manifest,args.pixel_threshold,args.allowed_changed_percent,args.diff_dir);write_report(report,args.report);print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2));return 0 if report['success'] else 1
if __name__=='__main__':raise SystemExit(main())
