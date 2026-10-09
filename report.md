# P2 Report — Crypto Inventory & Migration Planner

## What changed?
The inventory was scored with the configured lookup tables, and each asset received a migration recommendation and phase. The same marked-state Grover circuit was compiled and executed on both provisional processor definitions.

## Which architectural property changed?
Processor A uses coupling edges [[0, 1], [0, 2], [0, 3], [3, 4]]; Processor B uses coupling edges [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [1, 4], [2, 5]]. These are image-derived provisional transcriptions, not organizer-verified edge lists. The basis gates and placeholder noise parameters were held constant.

## Did transpilation add routing?
Using the all-to-all baseline, both provisional configurations compiled to 45 counted two-qubit gates versus 24 baseline, for an estimated SWAP overhead of 7. This estimate divides extra counted two-qubit gates by three; it is not a direct count of inserted SWAP instructions.

## How many extra operations?
The recorded outputs show 276 total compiled operations for each processor and 21 extra counted two-qubit gates versus baseline for each.

## Did the problem metric change?
In the current recorded run, the measured success probabilities for state `101` were 0.583496 ± 0.010893 for both Processor A and Processor B. The difference (B − A) was 0.000000. The recorded ideal reference probability was 0.952637 for both. Therefore, these results do **not** demonstrate a measured performance difference between the two provisional configurations.

## What should be investigated?
The identical results may reflect the selected logical circuit, transpiler choices, the provisional coupling maps, or the shared placeholder noise model. Re-run and inspect the compiled circuits and metric-generation path before drawing conclusions about topology. Do not claim that one processor outperformed the other unless regenerated evidence supports that claim.

## Could gate-set/noise differences also contribute?
Yes. This run keeps basis gates and placeholder noise parameters identical. Official basis gates, ports, calibration, noise, coupling directionality, or compiler constraints could affect outcomes and must be documented separately once authoritative configuration data is available.

## Why do both components belong in this project?
The inventory planner answers which cryptographic assets an organization should migrate first. The Grover experiment addresses a separate architecture question: how processor configuration affects execution of the same quantum solution. It is not a measurement of the cost of attacking real RSA or ECC implementations.

## What remains uncertain?
Processor definitions and noise values remain provisional until the official Challenge Kit specifications are supplied. Runtime is environment-dependent. The SWAP value is an estimate rather than a direct decomposition count.

## Limitations
A toy three-qubit Grover run does not estimate the cost of attacking real RSA/ECC keys. It is an educational architecture comparison, not a cryptanalytic forecast.
