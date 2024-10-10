from typing import Any, Dict, Optional
from .errors import HAMError
from .vector_clock import VectorClock, validate_type, validate_vector_clock

class State:
    @staticmethod
    def is_state(node: Dict[str, Any], key: str) -> bool:
        validate_type(node, dict)
        validate_type(key, str)
        return (node and '_' in node and '>' in node['_'] and 
                key in node['_']['>'] and isinstance(node['_']['>'][key], VectorClock))

    @staticmethod
    def ify(node: Dict[str, Any], key: str, state: VectorClock, val: Any = None, soul: Optional[str] = None) -> Dict[str, Any]:
        validate_type(node, dict)
        validate_type(key, str)
        validate_vector_clock(state)
        if not node or '_' not in node:
            raise HAMError('Invalid node structure')
        
        states = node['_'].setdefault('>', {})
        if key not in states or state.compare(states[key]) == 1:
            states[key] = state
            if val is not None:
                node[key] = val
                if soul:
                    node['_']['#'] = soul
        return node

    @staticmethod
    def get_state(node: Dict[str, Any], key: str) -> VectorClock:
        validate_type(node, dict)
        validate_type(key, str)
        return (node.get('_', {}).get('>', {}).get(key) or VectorClock())
