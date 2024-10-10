# amnesia-machine

A robust implementation of the Hypothetical Amnesia Machine (HAM) algorithm with Vector Clocks for advanced conflict resolution in distributed systems.

*see [amnesia-machine-js](https://github.com/firesight-ai/amnesia-machine-js) for the Javascript port.*

## Introduction

amnesia-machine is an advanced implementation of the Hypothetical Amnesia Machine (HAM) algorithm, designed to provide robust conflict resolution for distributed systems. It extends the original HAM concept by incorporating Vector Clocks, offering more precise handling of concurrent updates in a distributed environment.

This library is particularly useful for developers working with decentralized applications, peer-to-peer systems, or any scenario where data consistency across distributed nodes is crucial.

## Features

- Vector Clock-based conflict resolution
- Compatibility with Gun's data structures
- Deduplication mechanism
- Graph operations for distributed data
- Custom error handling
- Debug mode for easier troubleshooting
- Conversion utilities between Gun's state format and Vector Clocks

## Installation

```bash
poetry add amnesia-machine
```

## Usage

Here's a basic example of how to use amnesia-machine:

```python
from amnesia_machine import HAM, VectorClock

# Initialize HAM with a unique node ID
ham = HAM('node1')

# Create some vector clocks
machine_state = VectorClock({'node1': 1})
incoming_state = VectorClock({'node2': 1})
current_state = VectorClock({'node1': 1})

# Resolve a conflict
result = ham.ham(machine_state, incoming_state, current_state, 'incoming value', 'current value')

print(result)
```

## API Reference

### HAM Class

#### `__init__(node_id: str)`
- Initializes a new HAM instance with the given node ID.

#### `ham(machine_state: VectorClock, incoming_state: VectorClock, current_state: VectorClock, incoming_value: Any, current_value: Any) -> Dict[str, Any]`
- Resolves conflicts based on the HAM algorithm and Vector Clock comparisons.

#### `union(vertex: Dict[str, Any], node: Dict[str, Any]) -> Dict[str, Any]`
- Merges two nodes, resolving conflicts using the HAM algorithm.

#### `graph(graph: Dict[str, Any], soul: str, key: str, val: Any, state: VectorClock) -> Dict[str, Any]`
- Performs a graph operation, updating the given key-value pair with the provided state.

#### `set_debug_mode(mode: bool) -> None`
- Enables or disables debug mode for detailed logging.

### VectorClock Class

#### `__init__(clock: Dict[str, int] = None)`
- Creates a new Vector Clock instance.

#### `increment(node_id: str) -> None`
- Increments the clock for the specified node.

#### `merge(other_clock: VectorClock) -> None`
- Merges this clock with another Vector Clock.

#### `compare(other_clock: VectorClock) -> Optional[int]`
- Compares this clock with another Vector Clock.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Attribution

The Hypothetical Amnesia Machine is an invention of Mark Nadal. It was originally created to facilitate conflict resolution in [gundb](https://github.com/amark/gun)

## License

This project is licensed under the Apache-2.0 License.
