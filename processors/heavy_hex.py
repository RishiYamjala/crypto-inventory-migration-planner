"""Heavy-hex fragment checker and candidate Processor B variants.

Why this exists
---------------
A heavy-hex layout is a hexagonal lattice with one extra qubit placed on every
edge. Two consequences follow, and both are easy to test:

* no qubit has more than three neighbours, and
* the shortest loop has 12 qubits, so there are no triangles or other short
  cycles (the graph is bipartite).

The committed ``processor_B.json`` (Phase 1) has two triangles and one qubit
with four neighbours, so it is *heavy-hex-inspired* only loosely. This module
does not change it. It adds a checker plus two candidate variants that really
are pieces of a heavy-hex lattice, so the difference can be studied openly.

Because the shortest heavy-hex loop is 12 qubits, any 7- or 9-qubit piece is a
tree. That is a property of the geometry, not a design choice.

All variants are participant-defined research models. They are not organizer
files and not hardware calibration data.
"""
from pathlib import Path
import json

import networkx as nx
from networkx.algorithms import isomorphism

BASIS_GATES = ["rz", "sx", "x", "cx"]
NOISE = {
    "one_qubit_depolarizing": 0.001,
    "cx_depolarizing": 0.005,
    "readout_error": 0.01,
}

# 7 qubits: the "H" shape used by 7-qubit heavy-hex devices.
EDGES_7Q = [[0, 1], [1, 2], [1, 3], [3, 5], [4, 5], [5, 6]]
# 9 qubits: the same H, extended by one qubit on each of two branch ends.
EDGES_9Q = [[0, 1], [1, 2], [1, 3], [3, 5], [4, 5], [5, 6], [6, 7], [2, 8]]

VARIANTS = {7: EDGES_7Q, 9: EDGES_9Q}


def heavy_hex_patch(rows=3, cols=3):
    """Return a patch of the heavy-hex lattice (hex lattice, every edge subdivided)."""
    hexagonal = nx.hexagonal_lattice_graph(rows, cols)
    patch = nx.Graph()
    for u, v in hexagonal.edges:
        middle = ("edge", u, v)
        patch.add_edge(u, middle)
        patch.add_edge(middle, v)
    return patch


def to_graph(edges, num_qubits):
    graph = nx.Graph()
    graph.add_nodes_from(range(num_qubits))
    graph.add_edges_from(map(tuple, edges))
    return graph


def is_heavy_hex_fragment(edges, num_qubits, patch=None):
    """True if the coupling map is a connected piece of a heavy-hex lattice."""
    graph = to_graph(edges, num_qubits)
    if not nx.is_connected(graph):
        return False
    if max(dict(graph.degree).values(), default=0) > 3:
        return False
    patch = patch if patch is not None else heavy_hex_patch()
    matcher = isomorphism.GraphMatcher(patch, graph)
    return matcher.subgraph_is_monomorphic()


def graph_properties(edges, num_qubits):
    graph = to_graph(edges, num_qubits)
    return {
        "undirected_edge_count": graph.number_of_edges(),
        "triangle_count": sum(nx.triangles(graph).values()) // 3,
        "diameter": nx.diameter(graph),
    }


def build_variant(num_qubits):
    if num_qubits not in VARIANTS:
        raise ValueError(f"No heavy-hex variant defined for {num_qubits} qubits")
    edges = [list(edge) for edge in VARIANTS[num_qubits]]
    if not is_heavy_hex_fragment(edges, num_qubits):
        raise ValueError("variant is not a heavy-hex fragment")
    return {
        "name": f"Processor B heavy-hex candidate ({num_qubits} qubits)",
        "num_qubits": num_qubits,
        "coupling_map": edges,
        "basis_gates": list(BASIS_GATES),
        "ports": {"readout": "standard", "control": "standard"},
        "noise": dict(NOISE),
        "topology_description": (
            f"{num_qubits}-qubit connected piece of a heavy-hex lattice: every qubit has at most "
            "three neighbours and there are no triangles. Because the shortest heavy-hex loop is "
            "12 qubits, this piece is a tree."
        ),
        "stage": "Provisional comparison variant (not a replacement for Phase 1 Processor B)",
        "source": "participant-defined research model; qubit count must be confirmed with the organizers",
        "graph_properties": graph_properties(edges, num_qubits),
        "heavy_hex_check": {"is_heavy_hex_fragment": True, "max_degree": 3},
        "official_challenge_kit_verified": False,
        "note": (
            "Participant-defined research model. Not an organizer-issued edge list and not "
            "calibrated hardware. Noise values are the same simulator assumptions as Phase 1."
        ),
    }


def write_variants(directory=None):
    directory = Path(directory or Path(__file__).parent)
    paths = []
    for num_qubits in sorted(VARIANTS):
        path = directory / f"processor_B_heavyhex_{num_qubits}q.json"
        path.write_text(json.dumps(build_variant(num_qubits), indent=2) + "\n", encoding="utf-8")
        paths.append(path)
    return paths


if __name__ == "__main__":
    for written in write_variants():
        print(written)
