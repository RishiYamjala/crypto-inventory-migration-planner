# ⚛️ Crypto Inventory & Migration Planner

> **Qiskit Fall Fest 2026 · Phase 1 · Problem Statement P2**
>
> Turn cryptographic inventory into a quantum-risk migration plan—and measure how the **same Grover benchmark** behaves on two processor topologies.

[![Qiskit](https://img.shields.io/badge/Qiskit-Phase%201-6929C4?logo=qiskit&logoColor=white)](https://www.ibm.com/quantum/qiskit) [![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![Reproducible](https://img.shields.io/badge/experiment-reproducible-20B26B)](#reproducibility) [![AI disclosed](https://img.shields.io/badge/AI%20assistance-disclosed-555555)](#ai-assistance-disclosure)

## The thesis

**Inventory the cryptography, prioritize the migration, then measure—not guess—how processor geometry changes a quantum workload.**

```text
┌────────────────────────┐       ┌─────────────────────────────┐
│ Classical crypto       │       │ Quantum architecture study  │
│ inventory              │       │                             │
│ risk score → phase     │       │ same Grover circuit         │
│ migration plan         │       │ A → transpile → execute     │
│                        │       │ B → transpile → execute     │
└────────────┬───────────┘       └──────────────┬──────────────┘
             │                                  │
             └──────────────┬───────────────────┘
                            ▼
                 evidence-based Phase 1 report
```

## What is inside

### Part A — Crypto inventory → migration plan

- Ten-row sample inventory in `data/raw/inventory.csv`
- Auditable vulnerability, sensitivity, lifespan, and risk scoring tables
- HNDL detection for long-lived public-key assets in exposed usages
- NIST-aligned recommendations using ML-KEM, ML-DSA, SLH-DSA, AES-256, AES-256-GCM, SHA-256, and SHA-3
- Phase-based migration prioritization

### Part B — Controlled A/B benchmark

- Three-qubit Grover search for marked state `101`
- Two iterations; all qubits measured
- Identical A/B conditions: `2048` shots, optimization level `1`, seed `42`, and shared noise model
- Measured success probability, uncertainty, depth, two-qubit gates, SWAP estimate, physical qubits, total operations, runtime, and ideal reference

### Part C — Architecture evidence

- Coupling graphs
- Logical circuit drawing
- Noisy performance chart with error bars
- Depth / two-qubit-gate / SWAP trade-off chart
- Machine-readable CSV evidence

## Verified run results

These values are generated from the result CSVs—not typed in by hand.

| Metric | Processor A | Processor B | B − A |
|---|---:|---:|---:|
| Success probability for `101` | `0.593750` | `0.735840` | `0.142090` |
| Standard error | `0.010853` | `0.009742` | `-0.001110` |
| Compiled depth | `147` | `56` | `-91` |
| Counted two-qubit gates | `45` | `24` | `-21` |
| Estimated SWAP overhead | `7.000000` | `0.000000` | `-7.000000` |
| Total compiled operations | `231` | `96` | `-135` |

**Interpretation:** under this placeholder topology and common noise model, Processor B produced fewer compiled operations and a higher measured success probability. This is evidence for this experiment—not a universal claim that more connectivity is always better. Gate sets, placement, routing, noise, calibration, and compiler choices can all contribute.

Full interpretation: [`report.md`](report.md) · Raw evidence: [`results/tables/`](results/tables/)

---

## Quick start

```bash
# Get the repository
git clone <your-github-repository-url>
cd crypto_inventory_migration_planner

# Isolate the environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install and run
python -m pip install --upgrade pip
pip install -r requirements.txt
jupyter notebook main.ipynb
```

In Jupyter, choose **Kernel → Restart Kernel and Run All Cells**.

For a headless run:

```bash
jupyter nbconvert --to notebook --execute main.ipynb \
  --output executed_main.ipynb --ExecutePreprocessor.timeout=600
```

## Repository map

```text
├── README.md                         ← this showcase
├── main.ipynb                        ← end-to-end experiment
├── requirements.txt                  ← environment specification
├── report.md                         ← measured analysis + limitations
├── data/raw/inventory.csv            ← sample crypto inventory
├── processors/processor_A.json       ← line topology placeholder
├── processors/processor_B.json       ← connected topology placeholder
├── src/problem.py                    ← scoring + migration logic
├── src/processors.py                 ← JSON loading + noise model
├── src/routing.py                    ← Grover + transpilation
├── src/metrics.py                    ← A/B metrics
├── src/visualization.py              ← figures
└── results/                          ← CSV and PNG evidence
```

## Reproducibility controls

| Control | Value |
|---|---:|
| Shots | `2048` |
| Seed | `42` |
| Transpiler optimization level | `1` |
| Marked state | `101` |
| Grover iterations | `2` |
| One-qubit depolarizing error | `0.001` |
| CX depolarizing error | `0.01` |
| Readout error | `0.01` |

The SWAP value is explicitly an **estimate**: extra compiled two-qubit gates divided by three.

## Outputs

### Tables

- [`inventory_scored.csv`](results/tables/inventory_scored.csv)
- [`migration_plan.csv`](results/tables/migration_plan.csv)
- [`processor_A_metrics.csv`](results/tables/processor_A_metrics.csv)
- [`processor_B_metrics.csv`](results/tables/processor_B_metrics.csv)
- [`AB_comparison.csv`](results/tables/AB_comparison.csv)
- [`final_comparison.csv`](results/tables/final_comparison.csv)

### Figures

- [`processor_A_graph.png`](results/figures/processor_A_graph.png)
- [`processor_B_graph.png`](results/figures/processor_B_graph.png)
- [`logical_vs_transpiled.png`](results/figures/logical_vs_transpiled.png)
- [`AB_performance.png`](results/figures/AB_performance.png)
- [`architecture_tradeoffs.png`](results/figures/architecture_tradeoffs.png)

## Phase 1 checklist

- [x] Exactly one Problem Statement: **P2 — Crypto Inventory & Migration Planner**
- [x] Inventory scorer and migration planner
- [x] Same logical benchmark on A and B
- [x] Controlled seeds, shots, compiler settings, and noise
- [x] Transpiled circuits and measured metrics
- [x] A/B comparison, figures, and evidence-based report
- [x] Limitations and AI assistance disclosure
- [ ] Replace placeholders with official Challenge Kit values before submission

## Important Challenge Kit note

The Challenge Guide says the **official Challenge Kit is authoritative** for processor definitions, coupling maps, noise assumptions, and PS-specific inputs. The included JSON files are clearly marked `PLACEHOLDER - REPLACE WITH CHALLENGE KIT VALUES`.

Before submission, replace `processors/processor_A.json` and `processors/processor_B.json`, then rerun the notebook. Do not manually edit measured CSVs or report values.

## Limitations

A toy three-qubit Grover run **does not estimate the cost of attacking real RSA or ECC keys**. This is an educational architecture comparison, not a cryptanalytic forecast.

## AI assistance disclosure

This project was built with an AI tool. The implementation was executed, checked, and corrected in a clean notebook run before packaging.

## License

No license has been selected yet. Add the license required by your team or hackathon before public release.

## Authorized discovery, not unrestricted scanning

The optional `src/discovery.py` module demonstrates a safer next step beyond a static spreadsheet. It scans only a directory explicitly supplied by the user, records the matching source file and evidence excerpt, and never performs network scanning or reads outside that directory.

Run the synthetic demonstration from the notebook, or use it directly:

```python
from src.discovery import discover_directory
assets = discover_directory("data/raw/authorized_test_env")
```

Use this only against infrastructure and files for which you have explicit authorization. The generated evidence table is [`discovered_assets.csv`](results/tables/discovered_assets.csv).

## Optional dashboard

The repository also includes a local Streamlit dashboard with three views:

- **Overview** — total assets, migration-assessment count, Phase 1 count, HNDL flags
- **Inventory & roadmap** — prioritized assets, role-aware risk rationale, evidence, and next step
- **Processor A/B** — measured benchmark comparison from the CSV outputs

Launch it with:

```bash
streamlit run app.py
```

## Why the classical and quantum parts belong together

The inventory planner answers: **which cryptographic assets should an organization migrate first, and why?** The Grover experiment answers a different Phase 1 question: **how does processor architecture change execution of the same quantum solution?** The benchmark is included because the challenge requires an A/B architecture comparison; it is not a measurement of an organization's real RSA/ECC attack cost and should never be presented as one.

## Validation before submission

Run the focused migration tests:

```bash
pytest -q tests/test_problem.py
```

The tests verify that:

- key-establishment assets receive ML-KEM recommendations;
- signature/authentication assets receive ML-DSA recommendations;
- TLS certificates can require both key-exchange and certificate-signature migration;
- every scored asset receives an explainable rationale and deterministic priority rank.

The repository has not received official Challenge Kit processor definitions in the supplied materials. Until those files are provided, the A/B numbers are reproducible **simulator results from clearly labeled placeholder processors**, not hardware measurements.
