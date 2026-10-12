"""Fresh bounded in-memory state; mutation validates the entire candidate first."""
from collections.abc import Mapping
import math
from .semantics import StateSnapshot
from .values import thaw_json,canonical_bytes,fingerprint,nonblank

class InMemorySession:
    def __init__(self,initial,execution_id):
        nonblank(execution_id)
        self.execution_id=execution_id
        self._values=thaw_json(initial.values);self._revision=0
    def snapshot(self):
        return StateSnapshot("state:"+fingerprint({"execution":self.execution_id,"revision":self._revision,
                            "values":self._values}),self._revision,self._values)
    def set_values(self,entity,updates):
        if entity not in self._values or not isinstance(updates,Mapping) or not updates:
            raise ValueError("registered state entity/update required")
        candidate=thaw_json(self._values)
        for field,value in updates.items():
            if field not in candidate[entity]:raise ValueError("registered state field required")
            old=candidate[entity][field]
            if isinstance(old,bool):
                if not isinstance(value,bool):raise ValueError("boolean state type")
            elif isinstance(old,(int,float)):
                if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
                    raise ValueError("finite numeric state type")
            elif not isinstance(value,type(old)):raise ValueError("state type")
            candidate[entity][field]=value
        if len(canonical_bytes(candidate))>65536:raise ValueError("state byte ceiling")
        self._values=candidate;self._revision+=1
        return self.snapshot()
