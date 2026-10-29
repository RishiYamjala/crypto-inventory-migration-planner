import json
from pathlib import Path

import pytest

from processors.heavy_hex import (
    BASIS_GATES,
    NOISE,
    VARIANTS,
    build_variant,
    heavy_hex_patch,
    is_heavy_hex_fragment,
    to_graph,
)

ROOT = Path(__file__).resolve().parents[1]


def test_patch_matches_heavy_hex_rules():
    import networkx as nx

    patch = heavy_hex_patch()
    assert max(dict(patch.degree).values()) == 3
    assert nx.is_bipartite(patch)
    assert min(len(cycle) for cycle in nx.minimum_cycle_basis(patch)) == 12


@pytest.mark.parametrize("num_qubits", sorted(VARIANTS))
def test_variants_are_heavy_hex_fragments(num_qubits):
    import networkx as nx

    edges = VARIANTS[num_qubits]
    assert is_heavy_hex_fragment(edges, num_qubits)
    graph = to_graph(edges, num_qubits)
    assert nx.is_connected(graph)
    assert max(dict(graph.degree).values()) <= 3
    assert sum(nx.triangles(graph).values()) == 0
    assert nx.is_tree(graph)


def test_checker_rejects_triangle_and_degree_four_graphs():
    triangle = [[0, 1], [1, 2], [0, 2]]
    star = [[0, 1], [0, 2], [0, 3], [0, 4]]
    disconnected = [[0, 1], [2, 3]]
    assert not is_heavy_hex_fragment(triangle, 3)
    assert not is_heavy_hex_fragment(star, 5)
    assert not is_heavy_hex_fragment(disconnected, 4)


@pytest.mark.parametrize("num_qubits", sorted(VARIANTS))
def test_committed_variant_json_matches_generator(num_qubits):
    path = ROOT / "processors" / f"processor_B_heavyhex_{num_qubits}q.json"
    assert json.loads(path.read_text(encoding="utf-8")) == build_variant(num_qubits)


@pytest.mark.parametrize("num_qubits", sorted(VARIANTS))
def test_variants_keep_phase1_gate_set_and_noise_and_stay_unofficial(num_qubits):
    config = build_variant(num_qubits)
    assert config["basis_gates"] == BASIS_GATES == ["rz", "sx", "x", "cx"]
    assert config["noise"] == NOISE
    assert config["official_challenge_kit_verified"] is False
    assert config["num_qubits"] == num_qubits


def test_unknown_qubit_count_is_rejected():
    with pytest.raises(ValueError):
        build_variant(8)
