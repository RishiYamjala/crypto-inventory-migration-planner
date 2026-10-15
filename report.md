# P2 Report — Crypto Inventory & Migration Planner

## Project scope

The project combines a static cryptographic inventory scanner and migration planner with a separate Qiskit A/B architecture experiment. The Grover experiment is an educational topology comparison; it does not estimate the cost of attacking real RSA/ECC keys.

## Scanner status

The scanner targets RSA, DSA, DH, and ECC-related evidence and records source path, line number, matched evidence, likely cryptographic role, and conditional NIST migration guidance. Hash-only and symmetric-only matches are excluded from the PS-P2 public-key scanner metric.

Run the public-repository scan with:

```powershell
python scripts/evaluate_public_repo.py --repo psf/requests --ref v2.34.2
```

Download time and scanner execution time are measured separately. Precision and recall must not be reported until all candidate findings and missed true positives in the declared audit scope have been checked against a complete, manually reviewed ground-truth set. Regex findings are candidates, not proof of a vulnerability.

## Processor models and topology rationale

- **Processor A:** 5 qubits, 4 undirected edges, 0 triangles, graph diameter 3. This is a branching tree with limited connectivity.
- **Processor B:** 9 qubits, 12 undirected edges, 2 triangles, graph diameter 4. Its triangles are on nodes 3-4-5 and 6-7-8. The local dense neighborhoods and additional chords are intentional design choices for examining connectivity effects.
- **Basis gates:** `rz`, `sx`, `x`, `cx`.
- **Controlled simulator settings:** 4096 shots, optimization level 1, seed 42, one-qubit depolarizing error 0.001, CX depolarizing error 0.005, readout error 0.01.

The guide does not provide official Processor A/B JSON files; participants are expected to design and justify coupling maps. The graphs are participant-defined research models. JSON edges are treated as undirected physical couplings and expanded in both directions for Qiskit. Noise values are simulator assumptions, not hardware calibration measurements.

## Benchmark evidence status

The topology and coupling-map interpretation changed after earlier result files were generated. Do not use older benchmark numbers. Execute every cell in `main.ipynb` from a clean environment to regenerate the A/B comparison, figures, stress-test table, report, and README result table. The CI workflow runs the notebook and uploads regenerated evidence as an artifact. Only those regenerated values should be cited.

## Interpretation rules

- Report measured success probability with its standard error, compiled depth, counted two-qubit gates, physical qubits, total operations, and runtime.
- Distinguish explicitly counted SWAP instructions from the estimated SWAP-equivalent proxy (extra two-qubit gates divided by three).
- Explain any tie using the actual transpiled circuit and graph properties; a tie on one workload does not imply identical graphs.
- Compare the required Grover workload separately from supplementary star, chain, and ring stress tests.
- Do not generalize a tiny three-qubit circuit to large-scale cryptanalysis or real hardware.

## Reproducibility and limitations

Install the pinned Python 3.12 dependencies from `requirements.txt`, run `python -m pytest -q`, `python validate_processors.py`, and execute `main.ipynb` in a clean kernel. The validator checks the participant-defined models' structure, graph properties, and guide settings; it does not authenticate hardware.

The scanner's precision and recall remain unverified until the manual ground-truth audit is complete. Benchmark results must be regenerated and reviewed for the revised topology before submission.
