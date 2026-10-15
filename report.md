# P2 Report — Crypto Inventory & Migration Planner

> **Artifact status:** The committed Grover metrics below are from a previous run (2048 shots, CX depolarizing error 0.01). Source settings now match the Phase 1 guide (4096 shots, CX depolarizing error 0.005). Re-run the notebook before treating those numbers as results for the current settings.

## What changed?
The inventory was scored with the specified lookup tables, and each asset received a migration recommendation and phase. The same marked-state Grover circuit was compiled and executed on both participant-defined research processor models. The latest organizer clarification defines Processor A as 5 qubits and Processor B as 9 qubits; coupling maps are participant-designed reference architectures, while exact official basis gates, ports, directionality, and noise values remain unspecified.

## Benchmark settings

The source configuration uses 4096 shots, optimization level 1, seed 42, one-qubit depolarizing error 0.001, CX depolarizing error 0.005, and readout error 0.01. The error values are illustrative simulator settings from the guide, not official hardware calibration data. The current checked-in numerical result tables have not yet been regenerated with these settings.

## PS-P2 public-repository scanner evaluation

The guide requires a public open-source repository scan and precision, recall, and scanner execution time. The local synthetic fixture alone does not satisfy this evaluation. Use `python scripts/evaluate_public_repo.py --repo psf/requests --ref main` to create candidate findings and a scan-time summary. Precision and recall remain pending until a complete manual ground-truth audit is recorded; the runner refuses to claim them from unreviewed detections. No public-repository scan or precision/recall result is claimed in this report yet.

## Which architectural property changed?
Processor A uses coupling edges [[0, 1], [0, 2], [0, 3], [3, 4]]; Processor B uses coupling edges [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [1, 4], [2, 5], [1, 7], [2, 8]]. The participant-selected basis gates and illustrative simulator noise parameters were held constant for this controlled comparison; they are not official calibration values.

## Did transpilation add routing?
Using the all-to-all baseline, Processor A compiled to 45 counted two-qubit gates versus 24 baseline, for an estimated SWAP overhead of 7.000000; explicit measured SWAP instructions were 0. Processor B compiled to 45 versus 24 baseline, for an estimated SWAP overhead of 7.000000; explicit measured SWAP instructions were 0. This distinguishes direct SWAP instructions from the estimate extra two-qubit gates divided by three.

## How many extra operations?
The total compiled operation counts were 276 for Processor A and 276 for Processor B; extra two-qubit counts versus baseline were 21 and 21.

## Did the problem metric change?
For this three-qubit Grover circuit, the fixed seed and optimizer selected equivalent routing metrics on the two research graphs; that is a legitimate result for this workload, not evidence that the graphs are identical. A topology-sensitive regression circuit is tested separately. The measured success probabilities for state `101` were 0.583496 ± 0.010893 for Processor A and 0.583496 ± 0.010893 for Processor B. The difference (B − A) was 0.000000. Ideal reference probabilities were 0.952637 and 0.952637.

## Could gate-set/noise differences also contribute?
Yes. This run keeps basis gates and the default placeholder noise model identical, but transpilation can produce different gate counts and layouts. If official processor data changes basis gates, ports, calibration, or noise, those factors can contribute and must be reported separately.

## Why both components belong in this project?
The inventory planner answers which cryptographic assets an organization should migrate first. The Grover experiment answers the separate Phase 1 architecture question: how processor topology changes execution of the same quantum solution. It is not a measurement of the cost of attacking real RSA or ECC implementations.

## What remains uncertain?
The latest organizer clarification confirms Processor A (5 qubits) and Processor B (9 qubits) for the online stage, while exact official edge lists, basis gates, ports, and noise values are not supplied. The current processor files are therefore participant-defined and provisional until any organizer-authenticated definitions or benchmark settings are supplied. Runtime is environment-dependent. The SWAP value is an estimate rather than a direct decomposition count.

## Supplementary topology stress test

The required three-qubit Grover benchmark produced identical A/B metrics in the committed run. Supplementary synthetic circuits show that topology effects can depend on the interaction pattern:

| Workload | A depth | B depth | A two-qubit gates | B two-qubit gates | A estimated SWAP-equivalents | B estimated SWAP-equivalents |
|---|---:|---:|---:|---:|---:|---:|
| Star | 4 | 16 | 4 | 4 | 0.000 | 0.000 |
| Chain | 26 | 26 | 8 | 8 | 1.000 | 1.000 |
| Ring | 42 | 26 | 12 | 9 | 2.000 | 1.000 |

The star workload compiles to lower depth on A, while the ring workload compiles to lower depth and fewer two-qubit gates on B; chain metrics match in this run. This supports a workload-specific interpretation rather than forcing the main Grover values to differ. The estimated SWAP-equivalent value is extra two-qubit gates over an all-to-all baseline divided by three; it is a proxy, not a direct SWAP-instruction count. These are supplementary compiler/simulator results using participant-defined models, not official hardware measurements.

Run `python -m src.architecture_stress` to regenerate the supplementary CSV. The notebook now reruns this stress suite and includes the results in the generated report.

## Limitations
A toy three-qubit Grover run does not estimate the cost of attacking real RSA/ECC keys. It is an educational architecture comparison, not a cryptanalytic forecast.
