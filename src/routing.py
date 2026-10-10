"""Grover construction and architecture-specific transpilation.

Qiskit's ``coupling_map`` is interpreted as directed. The image-derived JSON
files do not verify edge directionality, so this module passes the listed pairs
through unchanged as a reproducible research assumption. It must not be read
as an official hardware direction specification.
"""
from qiskit import QuantumCircuit, transpile


def build_grover_circuit(marked='101', iterations=2, measure=True):
    n = len(marked)
    qc = QuantumCircuit(n, n if measure else 0)
    qc.h(range(n))
    for _ in range(iterations):
        # Oracle for the marked bit string. Qubit order is explicit and stable.
        for q, bit in enumerate(reversed(marked)):
            if bit == '0': qc.x(q)
        qc.h(n-1)
        qc.mcx(list(range(n-1)), n-1)
        qc.h(n-1)
        for q, bit in enumerate(reversed(marked)):
            if bit == '0': qc.x(q)
        # Diffusion operator.
        qc.h(range(n)); qc.x(range(n)); qc.h(n-1)
        qc.mcx(list(range(n-1)), n-1)
        qc.h(n-1); qc.x(range(n)); qc.h(range(n))
    if measure: qc.measure(range(n), range(n))
    return qc


def transpile_for_processor(circuit, processor, seed=42, optimization_level=1):
    # The research configs intentionally preserve their listed edge direction;
    # no reverse-edge completion is fabricated here.
    return transpile(circuit, basis_gates=processor['basis_gates'], coupling_map=processor['coupling_map'], optimization_level=optimization_level, seed_transpiler=seed)
