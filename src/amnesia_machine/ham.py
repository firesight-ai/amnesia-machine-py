from typing import Any, Dict, Optional
from .errors import HAMError
from .vector_clock import VectorClock, validate_type, validate_vector_clock
from .state import State

class HAM:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.debug_mode = False

    def ham(self, machine_state: VectorClock, incoming_state: VectorClock, current_state: VectorClock, 
            incoming_value: Any, current_value: Any) -> Dict[str, Any]:
        validate_vector_clock(machine_state)
        validate_vector_clock(incoming_state)
        validate_vector_clock(current_state)

        comparison = incoming_state.compare(current_state)

        if machine_state.compare(incoming_state) == 1:
            return {"defer": True}
        if comparison == -1:
            return {"historical": True}
        if comparison == 1:
            return {"converge": True, "incoming": True}
        if comparison == 0:
            incoming_value = self.unwrap(incoming_value)
            current_value = self.unwrap(current_value)
            if incoming_value == current_value:
                return {"state": True}
            if str(incoming_value) < str(current_value):
                return {"converge": True, "current": True}
            if str(current_value) < str(incoming_value):
                return {"converge": True, "incoming": True}
        return {"err": HAMError(f"Concurrent updates detected: {incoming_value} and {current_value}")}

    def unwrap(self, val: Any) -> Any:
        if isinstance(val, dict) and '#' in val and '.' in val and '>' in val:
            return val.get(':')
        return val

    def union(self, vertex: Dict[str, Any], node: Dict[str, Any]) -> Dict[str, Any]:
        validate_type(vertex, dict)
        validate_type(node, dict)

        if not vertex:
            return node
        if not node:
            return vertex

        machine_state = self.machine_state()

        if node.get('_', {}).get('#'):
            vertex.setdefault('_', {})['#'] = node['_']['#']

        for key, value in node.items():
            if key == '_':
                continue

            incoming_state = State.get_state(node, key)
            current_state = State.get_state(vertex, key)
            incoming_value = node[key]
            current_value = vertex.get(key)

            result = self.ham(machine_state, incoming_state, current_state, incoming_value, current_value)

            if 'err' in result:
                self.log('error', str(result['err']))
                continue

            if result.get('state') or result.get('historical') or result.get('current'):
                continue

            if result.get('defer') or result.get('incoming'):
                State.ify(vertex, key, incoming_state, incoming_value)

        return vertex

    def machine_state(self) -> VectorClock:
        state = VectorClock()
        state.increment(self.node_id)
        return state

    def graph(self, graph: Dict[str, Any], soul: str, key: str, val: Any, state: VectorClock) -> Dict[str, Any]:
        validate_type(graph, dict)
        validate_type(soul, str)
        validate_type(key, str)
        validate_vector_clock(state)
        graph[soul] = State.ify(graph.get(soul, {}), key, state, val, soul)
        return graph

    def graph_operation(self, graph: Dict[str, Any], soul: str, key: str, val: Any, state: VectorClock) -> Dict[str, Any]:
        validate_type(graph, dict)
        validate_type(soul, str)
        validate_type(key, str)
        validate_vector_clock(state)

        if soul not in graph:
            graph[soul] = {'_': {'#': soul, '>': {}}}

        return self.graph(graph, soul, key, val, state)

    def log(self, level: str, message: str) -> None:
        if self.debug_mode:
            print(f"[HAM {level.upper()}] {message}")

    def set_debug_mode(self, mode: bool) -> None:
        self.debug_mode = mode

    def merge_graphs(self, local_graph: Dict[str, Any], incoming_graph: Dict[str, Any]) -> Dict[str, Any]:
        validate_type(local_graph, dict)
        validate_type(incoming_graph, dict)

        merged_graph = local_graph.copy()

        for soul, node in incoming_graph.items():
            if soul == '_':
                continue

            if soul not in merged_graph:
                merged_graph[soul] = node
            else:
                merged_graph[soul] = self.union(merged_graph[soul], node)

        return merged_graph
