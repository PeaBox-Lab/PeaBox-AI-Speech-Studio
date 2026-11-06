import argparse,uuid
from peabox_voice_studio.config import OUTPUTS_DIR
from peabox_voice_studio.providers.catalog import KOKORO_LANGS
from peabox_voice_studio.providers.kokoro import generate
from peabox_voice_studio.services.files import safe_filename
from peabox_voice_studio.services.worker_queue import list_queue,recover_stale,run_one

def local_renderer(item,name):return generate(item['text'],item['voice'],KOKORO_LANGS.get(item['language'],'en-us'),item['speed'],safe_filename(name))
def main():
 parser=argparse.ArgumentParser(description='PeaBox local Kokoro worker');parser.add_argument('--once',action='store_true',help='Process one queued job and exit');parser.add_argument('--queue-id');args=parser.parse_args();worker_id=f'local-{uuid.uuid4().hex[:8]}';recover_stale();queue=[x for x in list_queue() if x['state'] in {'queued','partial','failed'}]
 if args.queue_id:queue=[x for x in queue if x['queue_id']==args.queue_id]
 if not queue:print('No queued local jobs.');return 0
 for envelope in reversed(queue):run_one(envelope['queue_id'],worker_id,{'Kokoro local':local_renderer});print(f"Completed {envelope['queue_id']}")
 return 0
if __name__=='__main__':raise SystemExit(main())
