from copy import deepcopy

from qiskit import QuantumCircuit

from src.metrics import _two_qubit_count
from src.processors import build_noise_model, load_processor
from src.routing import transpile_for_processor
from src.problem import algorithm_role, migration_for


def test_processor_maps_can_change_transpilation_metrics():
    a = load_processor("processors/processor_A.json")
    b = load_processor("processors/processor_B.json")
    circuit = QuantumCircuit(3)
    # A triangle/ring forces routing choices that expose the different graphs.
    circuit.cx(0, 1)
    circuit.cx(1, 2)
    circuit.cx(0, 2)
    compiled_a = transpile_for_processor(circuit, a)
    compiled_b = transpile_for_processor(circuit, b)
    assert a["coupling_map"] != b["coupling_map"]
    assert (compiled_a.depth(), _two_qubit_count(compiled_a)) != (compiled_b.depth(), _two_qubit_count(compiled_b))


def test_noise_model_uses_processor_parameters_and_basis_gates():
    a = load_processor("processors/processor_A.json")
    altered = deepcopy(a)
    altered["basis_gates"] = ["rz", "sx", "x", "cx"]
    altered["noise"] = {"one_qubit_depolarizing": 0.2, "cx_depolarizing": 0.3, "readout_error": 0.25}
    original = build_noise_model(a).to_dict()
    changed = build_noise_model(altered).to_dict()
    assert original != changed
    assert {"rz", "sx", "x", "cx"}.issubset({op for error in changed["errors"] for op in error.get("operations", [])})


def test_rsa_role_is_not_inferred_as_key_exchange_from_vpn_usage():
    role = algorithm_role("RSA-2048", "VPN")
    recommendation, _ = migration_for({"asset_name": "Legacy VPN", "algorithm": "RSA-2048", "usage": "VPN"})
    assert "requires confirmation" in role
    assert "Confirm RSA role" in recommendation
