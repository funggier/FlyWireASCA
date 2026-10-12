"""Bounded inference transport; a late worker never owns a later request."""
from dataclasses import dataclass,field
import json
import math
import threading
import time
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from ..budgets import CancelledStop

class TransportCancelled(CancelledStop):
    pass
class TransportBusy(RuntimeError):
    pass

class BoundedWorkerGate:
    def __init__(self):
        self._lock=threading.Lock();self._busy=False
    @property
    def busy(self):
        with self._lock:return self._busy
    def run(self,operation,*,deadline,cancellation):
        if cancellation.cancelled():raise TransportCancelled("cancelled before worker")
        if time.monotonic()>=deadline:raise TimeoutError("deadline before worker")
        with self._lock:
            if self._busy:raise TransportBusy("previous worker still in flight")
            self._busy=True
        ready=threading.Event();packet={};abandoned=threading.Event()
        def work():
            try:
                result=operation()
                if not abandoned.is_set():packet["result"]=result
            except BaseException as exc:
                if not abandoned.is_set():packet["error"]=exc
            finally:
                with self._lock:self._busy=False
                ready.set()
        threading.Thread(target=work,daemon=True).start()
        while True:
            if cancellation.cancelled():
                abandoned.set();raise TransportCancelled("in-flight request cancelled; residual cost unknown")
            remaining=deadline-time.monotonic()
            if remaining<=0:
                abandoned.set();raise TimeoutError("in-flight deadline; residual cost unknown")
            if ready.wait(min(.01,remaining)):
                if cancellation.cancelled() or time.monotonic()>=deadline:continue
                if "error" in packet:raise packet["error"]
                return packet["result"]

@dataclass
class TransportLog:
    records:list=field(default_factory=list)
    def append(self,**record):self.records.append(record)
    @property
    def generation_dispatches(self):
        return sum(r["path"]=="/api/chat" and r["event"]=="DISPATCH" for r in self.records)

class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,request,fp,code,msg,headers,newurl):
        raise ValueError("configured inference endpoint redirected")

class DeadlineJsonTransport:
    ALLOWED={("GET","/api/version"),("GET","/api/tags"),("POST","/api/show"),
             ("POST","/api/chat"),("POST","/api/embed")}
    def __init__(self,base_url,control,dispatch_log,*,opener=None,gate=None):
        parsed=urlsplit(base_url)
        if (parsed.scheme not in ("http","https") or not parsed.hostname
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in ("","/")):
            raise ValueError("base URL must be a configured inference origin")
        self.base_url=base_url.rstrip("/");self.control=control;self.log=dispatch_log
        self.gate=gate or BoundedWorkerGate()
        self.opener=opener or build_opener(_NoRedirect())
        self.override_deadline=None;self.override_cancellation=None
    def request_json(self,method,path,payload,timeout_seconds):
        if (method,path) not in self.ALLOWED:raise ValueError("unregistered inference endpoint")
        if not math.isfinite(timeout_seconds) or timeout_seconds<=0:raise ValueError("timeout")
        self.control.check_dispatch()
        remaining=self.control.ledger.deadline-self.control.clock.now()
        if self.override_deadline is not None:
            remaining=min(remaining,self.override_deadline-self.control.clock.now())
        timeout=min(float(timeout_seconds),remaining)
        cancellation=self.override_cancellation or self.control.cancellation
        deadline=time.monotonic()+max(0.0,timeout)
        # Explicitly refuse truncation while preserving the legacy adapter API.
        if path=="/api/chat":
            payload=dict(payload or {})
            payload["truncate"]=False
        data=None if payload is None else json.dumps(payload,ensure_ascii=False,allow_nan=False).encode("utf-8")
        if data is not None and len(data)>65536:raise ValueError("request size limit")
        request=Request(self.base_url+path,data=data,
                        headers={"Accept":"application/json","Content-Type":"application/json"},method=method)
        def operation():
            self.log.append(event="DISPATCH",path=path,run_id=self.control.run_id)
            with self.opener.open(request,timeout=max(.001,timeout)) as response:
                raw=response.read(16*1024*1024+1)
            if len(raw)>16*1024*1024:raise ValueError("response size limit")
            def pairs(values):
                result={}
                for key,value in values:
                    if key in result:raise ValueError("duplicate transport JSON field")
                    result[key]=value
                return result
            def nonfinite(value):raise ValueError("nonfinite JSON")
            value=json.loads(raw.decode("utf-8"),object_pairs_hook=pairs,parse_constant=nonfinite)
            if not isinstance(value,dict):raise ValueError("transport object required")
            return value
        try:
            result=self.gate.run(operation,deadline=deadline,cancellation=cancellation)
            self.control.check_dispatch()
            return result
        except (TimeoutError,TransportCancelled):
            self.log.append(event="ABORT",path=path,run_id=self.control.run_id,
                            outcome="CONTROL_RETURNED_LATE_WORKER_DISCARDED_RESIDUAL_COST_UNKNOWN")
            raise
