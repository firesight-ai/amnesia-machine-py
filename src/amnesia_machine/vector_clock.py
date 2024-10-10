from pydantic import BaseModel, Field
from typing import Dict, Optional, Set

class VectorClock(BaseModel):
    clock: Dict[str, int] = Field(default_factory=dict)

    def increment(self, node_id: str) -> None:
        self.clock[node_id] = self.clock.get(node_id, 0) + 1

    def merge(self, other_clock: 'VectorClock') -> None:
        for node_id, timestamp in other_clock.clock.items():
            if node_id not in self.clock or self.clock[node_id] < timestamp:
                self.clock[node_id] = timestamp

    def compare(self, other_clock: 'VectorClock') -> Optional[int]:
        is_greater = False
        is_less = False

        all_node_ids: Set[str] = set(self.clock.keys()) | set(other_clock.clock.keys())

        for node_id in all_node_ids:
            this_time = self.clock.get(node_id, 0)
            other_time = other_clock.clock.get(node_id, 0)

            if this_time > other_time:
                is_greater = True
            if this_time < other_time:
                is_less = True

        if is_greater and not is_less:
            return 1  # this happens-after other
        if is_less and not is_greater:
            return -1  # this happens-before other
        if not is_less and not is_greater:
            return 0  # equal
        return None  # concurrent

    @staticmethod
    def gun_state_to_vector_clock(gun_state: Dict[str, int]) -> 'VectorClock':
        return VectorClock(clock=gun_state)

    @staticmethod
    def vector_clock_to_gun_state(vector_clock: 'VectorClock') -> Dict[str, int]:
        return vector_clock.clock
