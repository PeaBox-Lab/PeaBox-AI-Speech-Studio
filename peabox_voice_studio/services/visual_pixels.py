import hashlib,json,zipfile
from io import BytesIO
from pathlib import Path
from PIL import Image,ImageChops,ImageEnhance
PNG_SIGNATURE=b'\x89PNG\r\n\x1a\n'
def sha256(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def validate_png(path,expected_size=None):
 path=Path(path);issues=[]
 if not path.is_file():return {'valid':False,'issues':['missing'],'path':str(path)}
 raw=path.read_bytes()
 if not raw.startswith(PNG_SIGNATURE):return {'valid':False,'issues':['not_png'],'path':str(path),'bytes':len(raw)}
 try:
  with Image.open(path) as image:image.verify()
  with Image.open(path) as image:size=image.size;mode=image.mode
 except Exception as exc:return {'valid':False,'issues':[f'decode:{type(exc).__name__}'],'path':str(path),'bytes':len(raw)}
 if expected_size and tuple(size)!=tuple(expected_size):issues.append(f'dimensions:{size[0]}x{size[1]} expected {expected_size[0]}x{expected_size[1]}')
 return {'valid':not issues,'issues':issues,'path':str(path),'bytes':len(raw),'width':size[0],'height':size[1],'mode':mode,'sha256':hashlib.sha256(raw).hexdigest()}
def manifest_index(manifest):
 sizes={x['name']:(x['width'],x['height']) for x in manifest['viewports']};return {x['filename']:{**x,'expected_size':sizes[x['viewport']]} for x in manifest['captures']}
def capture_inventory(directory,manifest):
 directory=Path(directory);index=manifest_index(manifest);rows=[]
 for filename,item in index.items():rows.append({**item,**validate_png(directory/filename,item['expected_size'])})
 extras=sorted(p.name for p in directory.glob('*.png') if p.name not in index)
 return {'directory':str(directory),'expected':len(index),'present':sum('missing' not in x['issues'] for x in rows),'valid':sum(x['valid'] for x in rows),'missing':[x['filename'] for x in rows if 'missing' in x['issues']],'invalid':[{'filename':x['filename'],'issues':x['issues']} for x in rows if not x['valid'] and 'missing' not in x['issues']],'extras':extras,'rows':rows,'ready':all(x['valid'] for x in rows) and not extras}
def _rgba(path):return Image.open(path).convert('RGBA')
def compare_png(baseline,candidate,pixel_threshold=0,allowed_changed_percent=0.0,diff_path=None):
 baseline=Path(baseline);candidate=Path(candidate);a=_rgba(baseline);b=_rgba(candidate)
 if a.size!=b.size:return {'passed':False,'reason':'dimension_mismatch','baseline_size':a.size,'candidate_size':b.size,'baseline':str(baseline),'candidate':str(candidate)}
 diff=ImageChops.difference(a,b);pixels=list(diff.getdata());total=len(pixels);changed=0;max_delta=0;sum_delta=0
 for pixel in pixels:
  delta=max(pixel);max_delta=max(max_delta,delta);sum_delta+=sum(pixel[:3])/3
  if delta>pixel_threshold:changed+=1
 percent=changed/total*100 if total else 0;mean_delta=sum_delta/total if total else 0;passed=percent<=allowed_changed_percent
 if diff_path is not None:
  diff_path=Path(diff_path);diff_path.parent.mkdir(parents=True,exist_ok=True);visual=ImageEnhance.Contrast(diff.convert('RGB')).enhance(4);visual.save(diff_path,'PNG')
 return {'passed':passed,'reason':'within_threshold' if passed else 'pixel_difference','width':a.width,'height':a.height,'total_pixels':total,'changed_pixels':changed,'changed_percent':round(percent,6),'pixel_threshold':pixel_threshold,'allowed_changed_percent':allowed_changed_percent,'max_channel_delta':max_delta,'mean_rgb_delta':round(mean_delta,4),'baseline_sha256':sha256(baseline),'candidate_sha256':sha256(candidate),'diff_path':str(diff_path) if diff_path else ''}
def compare_capture_set(baseline_dir,candidate_dir,manifest,pixel_threshold=0,allowed_changed_percent=0.0,diff_dir=None):
 baseline_dir=Path(baseline_dir);candidate_dir=Path(candidate_dir);diff_dir=Path(diff_dir) if diff_dir else None;results=[]
 for filename,item in manifest_index(manifest).items():
  base=baseline_dir/filename;cand=candidate_dir/filename;bv=validate_png(base,item['expected_size']);cv=validate_png(cand,item['expected_size'])
  if not bv['valid'] or not cv['valid']:results.append({'filename':filename,'page':item['page'],'viewport':item['viewport'],'passed':False,'reason':'invalid_capture','baseline_issues':bv['issues'],'candidate_issues':cv['issues']});continue
  result=compare_png(base,cand,pixel_threshold,allowed_changed_percent,(diff_dir/filename) if diff_dir else None);results.append({'filename':filename,'page':item['page'],'viewport':item['viewport'],**result})
 return {'schema':1,'baseline_hash':manifest.get('baseline_hash'),'pixel_threshold':pixel_threshold,'allowed_changed_percent':allowed_changed_percent,'captures':len(results),'passed':sum(x['passed'] for x in results),'failed':sum(not x['passed'] for x in results),'results':results,'success':all(x['passed'] for x in results)}
def write_report(report,path):path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2));return path
def diff_bundle(report):
 out=BytesIO()
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('pixel_diff_report.json',json.dumps(report,indent=2))
  for row in report.get('results',[]):
   path=Path(row.get('diff_path',''))
   if path.is_file():z.write(path,f"diffs/{path.name}")
 return out.getvalue()
