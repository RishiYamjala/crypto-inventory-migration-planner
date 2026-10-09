"""Check processor provenance before claiming Challenge Kit compliance."""
import json
from pathlib import Path


def validate_processor(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {"name", "num_qubits", "coupling_map", "basis_gates", "ports", "noise"}
    missing = required - data.keys()
    if missing:
        return False, f"{path}: missing fields {sorted(missing)}"
    if data.get("official_challenge_kit_verified") is not True:
        return False, f"{path}: official_challenge_kit_verified is not true"
    return True, f"{path}: verified"


if __name__ == "__main__":
    results = [validate_processor("processors/processor_A.json"), validate_processor("processors/processor_B.json")]
    for ok, message in results:
        print(message)
    raise SystemExit(0 if all(ok for ok, _ in results) else 1)
