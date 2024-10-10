import time
from pydantic import BaseModel, Field
from typing import Dict, Optional
from .vector_clock import VectorClock

class DupData(BaseModel):
    ts: int
    clock: VectorClock

class Dup(BaseModel):
    s: Dict[str, DupData] = Field(default_factory=dict)
    ttl: int = Field(default=300000)  # 5 minutes default

    def track(self, id: str) -> Optional[DupData]:
        if not id:
            return None
        if id not in self.s:
            self.s[id] = DupData(ts=int(time.time() * 1000), clock=VectorClock())
        return self.s[id]

    def check(self, id: str) -> Optional[DupData]:
        if not id:
            return None
        return self.s.get(id)

    def free(self) -> None:
        now = int(time.time() * 1000)
        self.s = {id: data for id, data in self.s.items() if data.ts and (now - data.ts) <= self.ttl}
