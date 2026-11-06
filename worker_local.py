import argparse,json,uuid
from peabox_voice_studio.providers.catalog import KOKORO_LANGS
from peabox_voice_studio.providers.kokoro import generate
from peabox_voice_studio.services.files import safe_filename
from peabox_voice_studio.services.worker_daemon import command,daemon_status,run_daemon
from peabox_voice_studio.services.worker_queue import list_queue,recover_stale,run_one

def local_renderer(item,name):return generate(item['text'],item['voice'],KOKORO_LANGS.get(item['language'],'en-us'),item['speed'],safe_filename(name))
def main():
 parser=argparse.ArgumentParser(description='PeaBox local Kokoro worker');group=parser.add_mutually_exclusive_group();group.add_argument('--once',action='store_true');group.add_argument('--daemon',action='store_true');group.add_argument('--status',action='store_true');group.add_argument('--pause',action='store_true');group.add_argument('--resume',action='store_true');group.add_argument('--drain',action='store_true');group.add_argument('--shutdown',action='store_true');parser.add_argument('--queue-id');parser.add_argument('--poll-seconds',type=float,default=2.0);args=parser.parse_args()
 if args.status:print(json.dumps(daemon_status(),indent=2));return 0
 for flag,mode in ((args.pause,'paused'),(args.resume,'running'),(args.drain,'draining'),(args.shutdown,'shutdown')):
  if flag:print(json.dumps(command(mode),indent=2));return 0
 worker_id=f'local-{uuid.uuid4().hex[:8]}';renderers={'Kokoro local':local_renderer}
 if args.daemon:return 0 if run_daemon(renderers,args.poll_seconds,worker_id) else 1
 recover_stale();queue=[x for x in list_queue() if x['state'] in {'queued','partial','failed'}]
 if args.queue_id:queue=[x for x in queue if x['queue_id']==args.queue_id]
 if not queue:print('No queued local jobs.');return 0
 for envelope in reversed(queue[:1] if args.once else queue):run_one(envelope['queue_id'],worker_id,renderers);print(f"Completed {envelope['queue_id']}")
 return 0
if __name__=='__main__':raise SystemExit(main())
