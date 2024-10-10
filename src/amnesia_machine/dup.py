import time
from typing import Dict, Optional
from .errors import HAMError
from .vector_clock import VectorClock, validate_type

class Dup:
    def __init__(self, options: Dict[str, int] = None):
        self.s: Dict[str, Dict[str, any]] = {}
        self.ttl: int = (options or {}).get('ttl', 300000)  # 5 minutes default

    def track(self, id: str) -> Optional[Dict[str, any]]:
        validate_type(id, str)
        if not id:
            return None
        if id not in self.s:
            self.s[id] = {'ts': int(time.time() * 1000), 'clock': VectorClock()}
        return self.s[id]

    def check(self, id: str) -> Optional[Dict[str, any]]:
        validate_type(id, str)
        if not id:
            return None
        return self.s.get(id)

    def free(self) -> None:
        now = int(time.time() * 1000)
        self.s = {id: data for id, data in self.s.items() if data['ts'] and (now - data['ts']) <= self.ttl}
