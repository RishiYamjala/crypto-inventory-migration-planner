# P2 Report — Crypto Inventory & Migration Planner

## What changed?
The inventory was scored with the specified lookup tables, and each asset received a migration recommendation and phase. The same marked-state Grover circuit was compiled and executed on both placeholder processor definitions.

## Which architectural property changed?
Processor A uses coupling edges [[0, 1], [1, 2], [2, 3], [3, 4]]; Processor B uses coupling edges [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [1, 4], [2, 5]]. The basis gates and noise parameters were held constant.

## Did transpilation add routing?
Using the all-to-all baseline, Processor A compiled to 45 counted two-qubit gates versus 24 baseline, for an estimated SWAP overhead of 7.000000. Processor B compiled to 45 versus 24 baseline, for an estimated SWAP overhead of 7.000000. This is an estimate because it divides extra two-qubit gates by three.

## How many extra operations?
The total compiled operation counts were 231 for Processor A and 276 for Processor B; extra two-qubit counts versus baseline were 21 and 21.

## Did the problem metric change?
The measured success probabilities for state `101` were 0.593750 ± 0.010853 for Processor A and 0.583496 ± 0.010893 for Processor B. The difference (B − A) was -0.010254. Ideal reference probabilities were 0.952637 and 0.952637.

## Could gate-set/noise differences also contribute?
Yes. This run keeps basis gates and the default placeholder noise model identical, but transpilation can produce different gate counts and layouts. If official processor data changes basis gates, ports, calibration, or noise, those factors can contribute and must be reported separately.

## Why both components belong in this project?
The inventory planner answers which cryptographic assets an organization should migrate first. The Grover experiment answers the separate Phase 1 architecture question: how processor topology changes execution of the same quantum solution. It is not a measurement of the cost of attacking real RSA or ECC implementations.

## What remains uncertain?
The processor definitions and noise values are placeholders until Challenge Kit values are supplied. Runtime is environment-dependent. The SWAP value is an estimate rather than a direct decomposition count.

## Limitations
A toy three-qubit Grover run does not estimate the cost of attacking real RSA/ECC keys. It is an educational architecture comparison, not a cryptanalytic forecast.
