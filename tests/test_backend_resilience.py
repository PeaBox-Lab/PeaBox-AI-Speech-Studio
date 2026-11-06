import time,unittest
from datetime import datetime,timedelta,timezone
from peabox_voice_studio.services.backend_resilience import BackendTimeout,CircuitBreaker,CircuitOpen,ResilientBackend,RetryPolicy,resilience_report
from peabox_voice_studio.services.storage_backends import MemoryBackend
class FlakyMemory(MemoryBackend):
 def __init__(self,failures=0,error=OSError):super().__init__();self.failures_left=failures;self.error=error;self.calls=0
 def get(self,*args):
  self.calls+=1
  if self.failures_left:self.failures_left-=1;raise self.error('fail')
  return super().get(*args)
class BackendResilienceTests(unittest.TestCase):
 def test_retry_succeeds_and_tracks_metrics(self):
  backend=FlakyMemory(2);backend.put('outputs','a',b'a');delays=[];wrapped=ResilientBackend(backend,RetryPolicy(3,.1,2),(CircuitBreaker()),1,sleep=delays.append);self.assertEqual(wrapped.get('outputs','a'),b'a');self.assertEqual(delays,[.1,.2]);self.assertEqual(wrapped.metrics.retries,2);self.assertEqual(wrapped.metrics.successes,1)
 def test_non_retryable_error_stops_immediately(self):
  backend=FlakyMemory(2,ValueError);backend.put('outputs','a',b'a');wrapped=ResilientBackend(backend,RetryPolicy(5,0,2),CircuitBreaker(),1,sleep=lambda _:None)
  with self.assertRaises(ValueError):wrapped.get('outputs','a')
  self.assertEqual(backend.calls,1);self.assertEqual(wrapped.metrics.retries,0)
 def test_retry_exhaustion_opens_circuit(self):
  backend=FlakyMemory(20);backend.put('outputs','a',b'a');circuit=CircuitBreaker(2,30);wrapped=ResilientBackend(backend,RetryPolicy(1,0,2),circuit,1,sleep=lambda _:None)
  for _ in range(2):
   with self.assertRaises(OSError):wrapped.get('outputs','a')
  self.assertEqual(circuit.state,'open')
  with self.assertRaises(CircuitOpen):wrapped.get('outputs','a')
 def test_half_open_success_closes_circuit(self):
  base=datetime(2026,1,1,tzinfo=timezone.utc);c=CircuitBreaker(1,10);c.failure(base);self.assertEqual(c.state,'open');c.allow(base+timedelta(seconds=10));self.assertEqual(c.state,'half_open');c.success();self.assertEqual(c.state,'closed')
 def test_half_open_allows_one_probe(self):
  base=datetime(2026,1,1,tzinfo=timezone.utc);c=CircuitBreaker(1,1);c.failure(base);c.allow(base+timedelta(seconds=2))
  with self.assertRaises(CircuitOpen):c.allow(base+timedelta(seconds=2))
 def test_half_open_failure_reopens(self):
  base=datetime(2026,1,1,tzinfo=timezone.utc);c=CircuitBreaker(1,1);c.failure(base);c.allow(base+timedelta(seconds=2));c.failure(base+timedelta(seconds=2));self.assertEqual(c.state,'open')
 def test_timeout_is_recorded(self):
  class Slow(MemoryBackend):
   def list(self,namespace=None):time.sleep(.05);return []
  wrapped=ResilientBackend(Slow(),RetryPolicy(1,0,2),CircuitBreaker(5,1),.005)
  with self.assertRaises(BackendTimeout):wrapped.list()
  self.assertEqual(wrapped.metrics.timeouts,1);self.assertEqual(wrapped.metrics.failures,1)
 def test_health_reports_audit(self):
  wrapped=ResilientBackend(MemoryBackend(),RetryPolicy(1,0,2),CircuitBreaker(),1);health=wrapped.health();self.assertTrue(health['healthy']);self.assertEqual(health['backend'],'memory');self.assertEqual(health['circuit']['state'],'closed')
 def test_resilience_report_combines_wrapped_backends(self):
  rows=resilience_report([ResilientBackend(MemoryBackend(),RetryPolicy(1,0,2),CircuitBreaker(),1)]);self.assertEqual(len(rows),1);self.assertTrue(rows[0]['healthy'])
 def test_policy_normalization(self):
  p=RetryPolicy(0,-1,.5).normalized();self.assertEqual(p.attempts,1);self.assertEqual(p.delay_seconds,0);self.assertEqual(p.backoff,1)
if __name__=='__main__':unittest.main()
