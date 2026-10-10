# Processor configuration status

## Sources checked

The shared organizer Drive folder was inspected on 2026-10-10:

<https://drive.google.com/drive/folders/1caxlXXeqjOkLmXGlimy_Etw0uPHSwyga>

The folder currently contains:

- `QFF_IBM_Hackathon_Guideline.pdf`
- `QFF_2026_Hackathon_Phase1_Participant_Instructions (1).pdf`
- `Challenge_Guide_Phase_1`

The downloaded copies are preserved in this repository's `docs/` directory with SHA-256 hashes recorded in Git history.

## Finding

The Participant Instructions say that each solution must run on the **exact processor definition supplied by the organizers** and that the Challenge Guide *may* contain Processor A/B definitions. The Challenge Guide's processor JSON on page 15 is explicitly an **illustrative example**:

```json
{
  "name": "processor_example",
  "num_qubits": 5,
  "coupling_map": [[0,1],[1,2],[2,3],[3,4]],
  "basis_gates": ["rz","sx","x","cx"],
  "ports": [0,4],
  "noise": {"type": "challenge_defined", "source": "official_challenge_kit"}
}
```

The same section says to replace every illustrative value with the exact organizer-supplied definition. It does not publish the real Processor A/B edge lists, basis gates, ports, or numerical noise parameters.

## Repository consequence

The repository confirms the online A/B requirements and records the visible 5-qubit/7-qubit stage information, but its local processor JSONs remain **unverified image-derived references**. `processors/challenge_kit_manifest.json` remains pending, and `python validate_processors.py` must continue to fail until the organizer supplies the actual definitions or an authenticated manifest.

Do not generate hashes from the current local JSONs and call them official. That would prove only local integrity, not organizer authenticity.

## Applicant archive finding

The uploaded `Applicants(QiskitFallFest2026).zip` contains only `chat.md` and `chat.txt`. It contains no JSON, ZIP, CSV, or configuration files. Its repeated hackathon announcement says:

> There is NO dataset or challenge kit to download.
>
> There is NO Processor A/B/C JSON file to download.
>
> Processor A and B topologies are for you to research and simulate — that IS the challenge.

This explains why the shared Drive has no exact processor files. The repository's models should therefore be described as **research simulations derived from the published architecture descriptions**, not as reconstructions of hidden official JSON files. The authenticity gate remains useful for preventing an unverified research model from being mislabeled as an official configuration, but the absence of a manifest is an organizer-scope finding rather than an incomplete download on this machine.
