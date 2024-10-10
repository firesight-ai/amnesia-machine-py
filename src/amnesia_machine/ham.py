from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from .errors import HAMError
from .vector_clock import VectorClock
from .state import State, NodeModel

class HAMResult(BaseModel):
    defer: Optional[bool] = None
    historical: Optional[bool] = None
    converge: Optional[bool] = None
    incoming: Optional[bool] = None
    state: Optional[bool] = None
    current: Optional[bool] = None
    err: Optional[HAMError] = None

class HAM(BaseModel):
    node_id: str
    debug_mode: bool = Field(default=False)

    def ham(self, machine_state: VectorClock, incoming_state: VectorClock, current_state: VectorClock, 
            incoming_value: Any, current_value: Any) -> HAMResult:
        comparison = incoming_state.compare(current_state)

        if machine_state.compare(incoming_state) == 1:
            return HAMResult(defer=True)
        if comparison == -1:
            return HAMResult(historical=True)
        if comparison == 1:
            return HAMResult(converge=True, incoming=True)
        if comparison == 0:
            incoming_value = self.unwrap(incoming_value)
            current_value = self.unwrap(current_value)
            if incoming_value == current_value:
                return HAMResult(state=True)
            if str(incoming_value) < str(current_value):
                return HAMResult(converge=True, current=True)
            if str(current_value) < str(incoming_value):
                return HAMResult(converge=True, incoming=True)
        return HAMResult(err=HAMError(f"Concurrent updates detected: {incoming_value} and {current_value}"))

    def unwrap(self, val: Any) -> Any:
        if isinstance(val, dict) and '#' in val and '.' in val and '>' in val:
            return val.get(':')
        return val

    def union(self, vertex: NodeModel, node: NodeModel) -> NodeModel:
        if not vertex:
            return node
        if not node:
            return vertex

        machine_state = self.machine_state()

        if node._.get('#'):
            vertex._.setdefault('#', node._['#'])

        for key, value in node.dict().items():
            if key == '_':
                continue

            incoming_state = State.get_state(node, key)
            current_state = State.get_state(vertex, key)
            incoming_value = value
            current_value = getattr(vertex, key, None)

            result = self.ham(machine_state, incoming_state, current_state, incoming_value, current_value)

            if result.err:
                self.log('error', str(result.err))
                continue

            if result.state or result.historical or result.current:
                continue

            if result.defer or result.incoming:
                State.ify(vertex, key, incoming_state, incoming_value)

        return vertex

    def machine_state(self) -> VectorClock:
        state = VectorClock()
        state.increment(self.node_id)
        return state

    def graph(self, graph: Dict[str, NodeModel], soul: str, key: str, val: Any, state: VectorClock) -> Dict[str, NodeModel]:
        graph[soul] = State.ify(graph.get(soul, NodeModel(_={})), key, state, val, soul)
        return graph

    def graph_operation(self, graph: Dict[str, NodeModel], soul: str, key: str, val: Any, state: VectorClock) -> Dict[str, NodeModel]:
        if soul not in graph:
            graph[soul] = NodeModel(_={'#': soul, '>': {}})

        return self.graph(graph, soul, key, val, state)

    def log(self, level: str, message: str) -> None:
        if self.debug_mode:
            print(f"[HAM {level.upper()}] {message}")

    def merge_graphs(self, local_graph: Dict[str, NodeModel], incoming_graph: Dict[str, NodeModel]) -> Dict[str, NodeModel]:
        merged_graph = local_graph.copy()

        for soul, node in incoming_graph.items():
            if soul == '_':
                continue

            if soul not in merged_graph:
                merged_graph[soul] = node
            else:
                merged_graph[soul] = self.union(merged_graph[soul], node)

        return merged_graph
