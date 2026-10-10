"""Processor JSON loading and common benchmark noise."""
import json
from pathlib import Path
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError


def load_processor(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def build_noise_model(processor):
    spec = processor['noise']
    model = NoiseModel()
    one = depolarizing_error(spec['one_qubit_depolarizing'], 1)
    two = depolarizing_error(spec['cx_depolarizing'], 2)
    readout = ReadoutError([[1-spec['readout_error'], spec['readout_error']], [spec['readout_error'], 1-spec['readout_error']]])
    two_qubit_gates = {'cx', 'cz', 'ecr', 'swap'}
    one_qubit_ops = [gate for gate in processor['basis_gates'] if gate not in two_qubit_gates]
    two_qubit_ops = [gate for gate in processor['basis_gates'] if gate in two_qubit_gates]
    if one_qubit_ops:
        model.add_all_qubit_quantum_error(one, one_qubit_ops)
    if two_qubit_ops:
        model.add_all_qubit_quantum_error(two, two_qubit_ops)
    model.add_all_qubit_readout_error(readout)
    return model
