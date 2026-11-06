import concurrent.futures,time
from dataclasses import dataclass,field
from datetime import datetime,timedelta,timezone
class BackendTimeout(TimeoutError):pass
class CircuitOpen(RuntimeError):pass
@dataclass
class RetryPolicy:
 attempts:int=3
 delay_seconds:float=.05
 backoff:float=2.0
 retryable:tuple=(OSError,TimeoutError,BackendTimeout)
 def normalized(self):return RetryPolicy(max(1,int(self.attempts)),max(0,float(self.delay_seconds)),max(1,float(self.backoff)),tuple(self.retryable))
@dataclass
class CircuitBreaker:
 failure_threshold:int=3
 recovery_seconds:float=30
 state:str='closed'
 failures:int=0
 opened_at:datetime|None=None
 half_open_calls:int=0
 def allow(self,at=None):
  at=at or datetime.now(timezone.utc)
  if self.state=='open':
   if self.opened_at and at>=self.opened_at+timedelta(seconds=self.recovery_seconds):self.state='half_open';self.half_open_calls=0
   else:raise CircuitOpen('Storage backend circuit is open')
  if self.state=='half_open' and self.half_open_calls>=1:raise CircuitOpen('Storage backend half-open probe already in progress')
  if self.state=='half_open':self.half_open_calls+=1
 def success(self):self.state='closed';self.failures=0;self.opened_at=None;self.half_open_calls=0
 def failure(self,at=None):
  self.failures+=1
  if self.state=='half_open' or self.failures>=self.failure_threshold:self.state='open';self.opened_at=at or datetime.now(timezone.utc);self.half_open_calls=0
 def snapshot(self):return {'state':self.state,'failures':self.failures,'failure_threshold':self.failure_threshold,'recovery_seconds':self.recovery_seconds,'opened_at':self.opened_at.isoformat() if self.opened_at else ''}
@dataclass
class BackendMetrics:
 calls:int=0
 successes:int=0
 failures:int=0
 retries:int=0
 timeouts:int=0
 total_seconds:float=0
 last_error:str=''
 last_operation:str=''
 def snapshot(self):return {'calls':self.calls,'successes':self.successes,'failures':self.failures,'retries':self.retries,'timeouts':self.timeouts,'average_ms':round(self.total_seconds/max(1,self.calls)*1000,2),'last_error':self.last_error,'last_operation':self.last_operation}
class ResilientBackend:
 def __init__(self,backend,retry_policy=None,circuit=None,timeout_seconds=10,sleep=time.sleep,clock=time.monotonic):self.backend=backend;self.name=f'resilient:{backend.name}';self.retry_policy=(retry_policy or RetryPolicy()).normalized();self.circuit=circuit or CircuitBreaker();self.timeout_seconds=max(.001,float(timeout_seconds));self.metrics=BackendMetrics();self.sleep=sleep;self.clock=clock
 def _timed(self,call):
  executor=concurrent.futures.ThreadPoolExecutor(max_workers=1);future=executor.submit(call)
  try:return future.result(timeout=self.timeout_seconds)
  except concurrent.futures.TimeoutError:future.cancel();raise BackendTimeout(f'Backend operation exceeded {self.timeout_seconds:g} seconds')
  finally:executor.shutdown(wait=False,cancel_futures=True)
 def _call(self,operation,*args,**kwargs):
  self.circuit.allow();policy=self.retry_policy;delay=policy.delay_seconds;self.metrics.calls+=1;self.metrics.last_operation=operation;started=self.clock();last=None
  try:
   for attempt in range(policy.attempts):
    try:
     result=self._timed(lambda:getattr(self.backend,operation)(*args,**kwargs));self.circuit.success();self.metrics.successes+=1;self.metrics.last_error='';return result
    except Exception as exc:
     last=exc
     if isinstance(exc,BackendTimeout):self.metrics.timeouts+=1
     retryable=isinstance(exc,policy.retryable)
     if not retryable or attempt==policy.attempts-1:break
     self.metrics.retries+=1;self.sleep(delay);delay*=policy.backoff
   self.circuit.failure();self.metrics.failures+=1;self.metrics.last_error=type(last).__name__;raise last
  finally:self.metrics.total_seconds+=max(0,self.clock()-started)
 def put(self,*a,**k):return self._call('put',*a,**k)
 def get(self,*a,**k):return self._call('get',*a,**k)
 def exists(self,*a,**k):return self._call('exists',*a,**k)
 def delete(self,*a,**k):return self._call('delete',*a,**k)
 def list(self,*a,**k):return self._call('list',*a,**k)
 def copy(self,*a,**k):return self._call('copy',*a,**k)
 def move(self,*a,**k):return self._call('move',*a,**k)
 def audit(self,*a,**k):return self._call('audit',*a,**k)
 def health(self):
  try:
   audit=self.audit();return {'backend':self.backend.name,'healthy':bool(audit.get('healthy',False)),'circuit':self.circuit.snapshot(),'metrics':self.metrics.snapshot(),'audit':audit}
  except Exception as exc:return {'backend':self.backend.name,'healthy':False,'error':type(exc).__name__,'circuit':self.circuit.snapshot(),'metrics':self.metrics.snapshot()}
 def status(self):return {'backend':self.backend.name,'circuit':self.circuit.snapshot(),'metrics':self.metrics.snapshot()}
def resilience_report(backends):return [backend.health() if hasattr(backend,'health') else {'backend':backend.name,'healthy':backend.audit().get('healthy',False)} for backend in backends]
