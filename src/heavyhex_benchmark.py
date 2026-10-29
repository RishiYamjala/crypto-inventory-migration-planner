"""Phase 2 comparison: Processors A and B versus the heavy-hex candidate variants.

Runs the *same* Phase 1 Grover benchmark (marked state ``101``, 4096 shots,
optimization level 1, seed 42, shared noise model) on four participant-defined
processor models:

* Processor A (Phase 1, 5 qubits)
* Processor B (Phase 1, 9 qubits, two triangles and one four-neighbour qubit)
* Processor B heavy-hex candidate, 7 qubits (a true heavy-hex fragment)
* Processor B heavy-hex candidate, 9 qubits (a true heavy-hex fragment)

It reuses ``run_processor_benchmark`` and the supplementary stress workloads
unchanged, so the numbers are directly comparable with the Phase 1 tables. The
Phase 1 outputs (``AB_comparison.csv`` and friends) are never modified.

All processors are participant-defined research models, not organizer files and
not calibrated hardware. Results are simulator/compiler metrics, not
real-hardware performance or cryptographic attack estimates.

Run from the repository root with: python -m src.heavyhex_benchmark
"""
from pathlib import Path

import pandas as pd
from qiskit import transpile

from .architecture_stress import SEED as STRESS_SEED, workload_circuits
from .metrics import (
    _measured_swap_count,
    _physical_qubits_used,
    _two_qubit_count,
    run_processor_benchmark,
)
from .processors import load_processor
from .routing import build_grover_circuit, transpile_for_processor

PROCESSOR_PATHS = {
    "Processor A": "processors/processor_A.json",
    "Processor B": "processors/processor_B.json",
    "Processor B heavy-hex 7q": "processors/processor_B_heavyhex_7q.json",
    "Processor B heavy-hex 9q": "processors/processor_B_heavyhex_9q.json",
}

COMPARISON_OUTPUT = Path("results/tables/phase2_heavyhex_comparison.csv")
STRESS_OUTPUT = Path("results/tables/phase2_heavyhex_stress_test.csv")


def load_all_processors(paths=None):
    """Return {label: processor_dict} in a stable, documented order."""
    paths = paths or PROCESSOR_PATHS
    return {label: load_processor(path) for label, path in paths.items()}


def run_heavyhex_comparison(marked="101", iterations=2, paths=None):
    """Run the shared Grover benchmark on every processor; one row each."""
    logical = build_grover_circuit(marked, iterations=iterations)
    rows = []
    for label, processor in load_all_processors(paths).items():
        row, _compiled, _baseline = run_processor_benchmark(logical, processor, marked=marked)
        properties = processor.get("graph_properties", {})
        rows.append(
            {
                "label": label,
                "num_qubits": processor["num_qubits"],
                "undirected_edges": properties.get("undirected_edge_count"),
                "triangles": properties.get("triangle_count"),
                "diameter": properties.get("diameter"),
                **row,
            }
        )
    return pd.DataFrame(rows)


def run_heavyhex_stress_test(paths=None):
    """Compile the supplementary stress workloads against every processor."""
    rows = []
    for workload_name, circuit in workload_circuits().items():
        for label, processor in load_all_processors(paths).items():
            compiled = transpile_for_processor(
                circuit, processor, seed=STRESS_SEED, optimization_level=1
            )
            baseline = transpile(
                circuit,
                basis_gates=processor["basis_gates"],
                coupling_map=None,
                seed_transpiler=STRESS_SEED,
                optimization_level=1,
            )
            baseline_two_qubit = _two_qubit_count(baseline)
            compiled_two_qubit = _two_qubit_count(compiled)
            extra_two_qubit = max(0, compiled_two_qubit - baseline_two_qubit)
            rows.append(
                {
                    "workload": workload_name,
                    "label": label,
                    "logical_qubits": circuit.num_qubits,
                    "compiled_depth": compiled.depth(),
                    "compiled_two_qubit_gates": compiled_two_qubit,
                    "baseline_two_qubit_gates": baseline_two_qubit,
                    "extra_two_qubit_gates": extra_two_qubit,
                    "measured_swap_instructions": _measured_swap_count(compiled),
                    "estimated_swap_equivalents": extra_two_qubit / 3,
                    "physical_qubits_used": _physical_qubits_used(compiled),
                    "seed": STRESS_SEED,
                    "interpretation": "supplementary compiler stress test; not a cryptographic attack estimate",
                }
            )
    return pd.DataFrame(rows)


def main():
    COMPARISON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    comparison = run_heavyhex_comparison()
    comparison.to_csv(COMPARISON_OUTPUT, index=False)
    print(comparison.drop(columns=["processor", "shots", "seed"]).to_string(index=False))
    print(f"\nSaved Grover comparison to {COMPARISON_OUTPUT}")

    stress = run_heavyhex_stress_test()
    stress.to_csv(STRESS_OUTPUT, index=False)
    print()
    print(stress.drop(columns=["interpretation", "seed"]).to_string(index=False))
    print(f"\nSaved supplementary stress test to {STRESS_OUTPUT}")


if __name__ == "__main__":
    main()
