"""Measured metrics for identical A/B benchmark runs."""
import math, time
from qiskit import transpile
from qiskit_aer import AerSimulator
from .processors import build_noise_model
from .routing import transpile_for_processor

SHOTS = 2048
SEED = 42


def _two_qubit_count(circuit):
    return sum(1 for instruction in circuit.data if instruction.operation.name in {'cx','cz','ecr','swap'} and len(instruction.qubits) == 2)


def _measured_swap_count(circuit):
    return sum(1 for instruction in circuit.data if instruction.operation.name == 'swap' and len(instruction.qubits) == 2)


def _physical_qubits_used(circuit):
    used = set()
    for instruction in circuit.data:
        used.update(circuit.find_bit(q).index for q in instruction.qubits)
    return len(used)


def _probability(counts, bitstring, shots):
    # Qiskit count keys are displayed with the highest classical bit first.
    return counts.get(bitstring, 0) / shots


def run_processor_benchmark(logical_circuit, processor, marked='101'):
    start = time.perf_counter()
    compiled = transpile_for_processor(logical_circuit, processor, seed=SEED, optimization_level=1)
    simulator = AerSimulator(noise_model=build_noise_model(processor), seed_simulator=SEED)
    result = simulator.run(compiled, shots=SHOTS, seed_simulator=SEED).result()
    elapsed = time.perf_counter() - start
    counts = result.get_counts()
    p = _probability(counts, marked, SHOTS)
    baseline = transpile(logical_circuit, basis_gates=processor['basis_gates'], coupling_map=None, optimization_level=1, seed_transpiler=SEED)
    compiled_2q, baseline_2q = _two_qubit_count(compiled), _two_qubit_count(baseline)
    extra_2q = max(0, compiled_2q - baseline_2q)
    ideal_sim = AerSimulator(seed_simulator=SEED)
    ideal_result = ideal_sim.run(baseline, shots=SHOTS, seed_simulator=SEED).result()
    ideal_p = _probability(ideal_result.get_counts(), marked, SHOTS)
    row = {
        'processor': processor['name'], 'success_probability':p,
        'std_error':math.sqrt(p*(1-p)/SHOTS), 'depth':compiled.depth(),
        'two_qubit_gates':compiled_2q, 'measured_swap_count':_measured_swap_count(compiled), 'swap_estimate':extra_2q/3,
        'physical_qubits_used':_physical_qubits_used(compiled), 'total_ops':sum(compiled.count_ops().values()),
        'runtime_seconds':elapsed, 'shots':SHOTS, 'seed':SEED, 'ideal_success_probability':ideal_p,
        'baseline_two_qubit_gates':baseline_2q, 'extra_two_qubit_gates':extra_2q,
    }
    return row, compiled, baseline


def compare_metrics(a, b):
    fields = ['success_probability','std_error','depth','two_qubit_gates','measured_swap_count','swap_estimate','physical_qubits_used','total_ops','runtime_seconds','shots','seed','ideal_success_probability','baseline_two_qubit_gates','extra_two_qubit_gates']
    rows = []
    for field in fields:
        av, bv = a[field], b[field]
        try: diff = bv - av
        except TypeError: diff = ''
        rows.append({'Metric':field, 'Processor A':av, 'Processor B':bv, 'Difference':diff})
    return rows
