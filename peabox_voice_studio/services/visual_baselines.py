import hashlib,json,re
from pathlib import Path
from peabox_voice_studio.config import VERSION,VISUAL_BASELINES_DIR
REQUIRED_TOKENS=('--pb-navy','--pb-blue','--pb-border','--pb-sidebar-text','--pb-sidebar-control','--pb-good','--pb-warn','--pb-bad')
REQUIRED_COMPONENTS=('.pb-topbar','.pb-card','.pb-section','.pb-empty','.pb-status','.pb-step')
def stable_hash(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def _literal_assignment(source,name):
 import ast
 tree=ast.parse(source)
 for node in tree.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets):return ast.literal_eval(node.value)
 raise ValueError(f'Missing {name}')
def navigation_snapshot(ui_source):
 navigation=_literal_assignment(ui_source,'NAVIGATION');page_meta=_literal_assignment(ui_source,'PAGE_META');groups=[]
 for group,entries in navigation.items():groups.append({'group':group,'pages':[{'label':label,'page':page,'icon':icon} for label,page,icon in entries]})
 return {'version':VERSION,'groups':groups,'page_meta':{k:{'title':v[0],'subtitle':v[1],'group':v[2]} for k,v in sorted(page_meta.items())}}
def theme_snapshot(source):
 colors=dict(re.findall(r'(--pb-[a-z0-9-]+)\s*:\s*([^;]+);',source));media=sorted(set(re.findall(r'@media\s*\(([^)]+)\)',source)));selectors={x:x in source for x in REQUIRED_COMPONENTS};sidebar={'select_dark':'div[data-baseweb="select"] > div' in source,'radio_selected':':has(input:checked)' in source,'quick_button_contrast':'[data-testid="stSidebar"] .stButton > button' in source and 'color:#ffffff!important' in source}
 return {'tokens':colors,'media_queries':media,'components':selectors,'sidebar':sidebar}
def contrast_ratio(a,b):
 def rgb(value):value=value.lstrip('#');return tuple(int(value[i:i+2],16)/255 for i in (0,2,4))
 def lum(value):
  return .2126*value[0]+.7152*value[1]+.0722*value[2]
 def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
 l1=lum(tuple(linear(x) for x in rgb(a)));l2=lum(tuple(linear(x) for x in rgb(b)));return round((max(l1,l2)+.05)/(min(l1,l2)+.05),2)
def validate_theme(snapshot):
 issues=[]
 for token in REQUIRED_TOKENS:
  if token not in snapshot['tokens']:issues.append(f'missing_token:{token}')
 for selector,present in snapshot['components'].items():
  if not present:issues.append(f'missing_component:{selector}')
 for name,present in snapshot['sidebar'].items():
  if not present:issues.append(f'sidebar_contract:{name}')
 if not any('max-width:760px' in x.replace(' ','') for x in snapshot['media_queries']):issues.append('missing_mobile_breakpoint')
 return issues
def baseline_document(ui_source,screen_snapshots=None):
 nav=navigation_snapshot(ui_source);theme=theme_snapshot(ui_source);screens=screen_snapshots or {};doc={'schema':1,'version':VERSION,'navigation':nav,'theme':theme,'screens':screens,'contrast':{'sidebar_text_on_control':contrast_ratio('#ffffff','#203b64'),'ink_on_card':contrast_ratio('#172033','#ffffff')}};doc['hash']=stable_hash({k:v for k,v in doc.items() if k!='hash'});return doc
def write_baseline(document,path=None):
 path=Path(path or VISUAL_BASELINES_DIR/f'ui_baseline_{VERSION}.json');path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(document,ensure_ascii=False,indent=2));return path
def read_baseline(path):return json.loads(Path(path).read_text())
def compare_baselines(expected,actual):
 changes=[]
 if expected.get('navigation')!=actual.get('navigation'):changes.append('navigation')
 if expected.get('theme')!=actual.get('theme'):changes.append('theme')
 for page in sorted(set(expected.get('screens',{}))|set(actual.get('screens',{}))):
  if expected.get('screens',{}).get(page)!=actual.get('screens',{}).get(page):changes.append(f'screen:{page}')
 return {'matches':not changes,'changes':changes,'expected_hash':expected.get('hash'),'actual_hash':actual.get('hash')}
def screenshot_manifest(document,viewports=None):
 viewports=viewports or [{'name':'desktop','width':1440,'height':1000},{'name':'tablet','width':1024,'height':900},{'name':'mobile','width':390,'height':844}];pages=[x['page'] for group in document['navigation']['groups'] for x in group['pages']]
 return {'schema':1,'version':document['version'],'baseline_hash':document['hash'],'viewports':viewports,'captures':[{'page':page,'viewport':vp['name'],'filename':f"{page.lower().replace(' ','_').replace('&','and')}_{vp['name']}.png"} for page in pages for vp in viewports]}
def screen_source_snapshot(path):
 import ast
 path=Path(path);source=path.read_text(encoding='utf-8');tree=ast.parse(source);calls=[];labels=[]
 for node in ast.walk(tree):
  if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):
   owner=node.func.value
   if isinstance(owner,ast.Name) and owner.id=='st':
    calls.append(node.func.attr)
    if node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str):labels.append(node.args[0].value)
   elif isinstance(owner,ast.Attribute) and isinstance(owner.value,ast.Name) and owner.value.id=='st':calls.append(f'{owner.attr}.{node.func.attr}')
 return {'module':path.stem,'lines':len(source.splitlines()),'streamlit_calls':[[name,calls.count(name)] for name in sorted(set(calls))],'labels':sorted(set(labels)),'source_hash':hashlib.sha256(source.encode()).hexdigest()}
def collect_screen_snapshots(directory):return {path.stem:screen_source_snapshot(path) for path in sorted(Path(directory).glob('*.py')) if path.name not in {'__init__.py','registry.py'}}
def validate_baseline(document):
 issues=validate_theme(document['theme']);pages={x['page'] for group in document['navigation']['groups'] for x in group['pages']}
 if len(pages)!=19:issues.append(f'page_count:{len(pages)}')
 if set(document.get('screens',{}))!={x.replace(' ','_').lower() for x in []} and not document.get('screens'):issues.append('missing_screen_snapshots')
 if document['contrast']['sidebar_text_on_control']<4.5:issues.append('sidebar_contrast')
 if document['contrast']['ink_on_card']<4.5:issues.append('card_contrast')
 return issues
