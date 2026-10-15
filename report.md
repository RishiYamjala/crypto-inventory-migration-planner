# P2 Report — Crypto Inventory & Migration Planner

## Project scope

The project combines a static cryptographic inventory scanner and migration planner with a separate Qiskit A/B architecture experiment. The Grover experiment is an educational topology comparison; it does not estimate the cost of attacking real RSA/ECC keys.

## Scanner status

The scanner targets RSA, DSA, DH, and ECC-related evidence and records source path, line number, matched evidence, likely cryptographic role, and conditional NIST migration guidance. Hash-only and symmetric-only matches are excluded from the PS-P2 public-key scanner metric.

The public-repository runner is:

```powershell
python scripts/evaluate_public_repo.py --repo psf/requests --ref v2.34.2
```

It records scan time separately from download time. **Precision and recall must not be reported until the candidate findings and missed true positives have been checked against a complete manually reviewed ground-truth set.** Regex findings are candidates, not proof of a vulnerability. The CI job uploads the public scan output for review.

## Processor models and rationale

- **Processor A:** five-qubit branching tree with four undirected edges.
- **Processor B:** nine-qubit connected graph with twelve undirected edges. It contains two local triangles, on nodes 0-1-2 and 4-5-6, to make local connectivity a measurable design property.
- **Basis gates:** `rz`, `sx`, `x`, `cx`.
- **Controlled simulator settings:** 4096 shots, optimization level 1, seed 42, one-qubit depolarizing error 0.001, CX depolarizing error 0.005, readout error 0.01.

The guide does not provide official Processor A/B JSON files; participants are expected to design and justify coupling maps. The graphs above are participant-defined research models. JSON edges are interpreted as undirected physical couplings and expanded in both directions for Qiskit. Noise values are controlled simulator assumptions, not hardware calibration measurements.

## Benchmark evidence status

The processor topology and edge-direction handling were changed after the previously committed result tables and figures were generated. **Those older metrics are stale and are not reported here as current results.** Run every cell in `main.ipynb` from a clean environment to regenerate the A/B comparison, figures, stress-test table, and this report. The CI workflow executes the notebook and uploads the resulting evidence as an artifact. Only the regenerated values should be used for submission.

## Interpretation rules

- Report measured success probability with its standard error, compiled depth, counted two-qubit gates, physical qubits, total operations, and runtime.
- Distinguish explicitly counted SWAP instructions from the estimated SWAP-equivalent proxy (extra two-qubit gates divided by three).
- Explain any tie using the actual transpiled circuit and topology; a tie on one workload does not imply identical graphs.
- Compare the required Grover workload separately from supplementary star, chain, and ring stress tests.
- Do not generalize a tiny three-qubit circuit to large-scale cryptanalysis or real hardware.

## Reproducibility and limitations

Install the pinned Python 3.12 dependencies from `requirements.txt`, run `python -m pytest -q`, `python validate_processors.py`, and execute `main.ipynb` in a clean kernel. The validator checks the participant-defined models' structure and guide settings; it does not authenticate hardware.

The scanner's precision/recall remains unverified until its manual ground-truth audit is complete. The benchmark metrics remain unverified for the revised topology until the notebook is rerun and its generated outputs are reviewed.
