from pydantic import BaseModel
from typing import Any, Dict, Optional
from .errors import HAMError
from .vector_clock import VectorClock

class NodeModel(BaseModel):
    _: Dict[str, Any]

class State:
    @staticmethod
    def is_state(node: NodeModel, key: str) -> bool:
        return (node and '_' in node.dict() and '>' in node._.get('>', {}) and 
                key in node._['>'] and isinstance(node._['>'][key], VectorClock))

    @staticmethod
    def ify(node: NodeModel, key: str, state: VectorClock, val: Any = None, soul: Optional[str] = None) -> NodeModel:
        if '_' not in node.dict():
            raise HAMError('Invalid node structure')
        
        states = node._.setdefault('>', {})
        if key not in states or state.compare(states[key]) == 1:
            states[key] = state
            if val is not None:
                node.__dict__[key] = val
                if soul:
                    node._['#'] = soul
        return node

    @staticmethod
    def get_state(node: NodeModel, key: str) -> VectorClock:
        return VectorClock(clock=node._.get('>', {}).get(key, {}))
