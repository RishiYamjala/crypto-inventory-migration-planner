"""Validate processor files against an organizer-supplied authoritative manifest.

The manifest is intentionally separate from the processor JSON files. A Boolean inside
an editable processor file cannot prove authenticity. The manifest must be obtained from
the organizer or Challenge Kit and must contain the exact expected values and hashes.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).parent
MANIFEST_PATH = ROOT / "processors" / "challenge_kit_manifest.json"
PROCESSORS = {"Processor A": ROOT / "processors" / "processor_A.json", "Processor B": ROOT / "processors" / "processor_B.json"}
REQUIRED_FIELDS = {"name", "num_qubits", "coupling_map", "basis_gates", "ports", "noise"}


def canonical_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_processor(name, path, manifest):
    if name not in manifest.get("processors", {}):
        return False, f"{name}: missing from authoritative manifest"
    expected = manifest["processors"][name]
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        return False, f"{name}: missing fields {sorted(missing)}"
    checks = {
        "num_qubits": data["num_qubits"] == expected.get("num_qubits"),
        "coupling_map": data["coupling_map"] == expected.get("coupling_map"),
        "basis_gates": data["basis_gates"] == expected.get("basis_gates"),
        "ports": data["ports"] == expected.get("ports"),
        "noise": data["noise"] == expected.get("noise"),
    }
    failed = [field for field, ok in checks.items() if not ok]
    if failed:
        return False, f"{name}: exact manifest comparison failed for {failed}"
    actual_hash = canonical_hash(path)
    if actual_hash != expected.get("config_sha256"):
        return False, f"{name}: SHA-256 mismatch (actual {actual_hash})"
    if data.get("official_challenge_kit_verified") is not True:
        return False, f"{name}: processor flag is not true"
    return True, f"{name}: verified against {manifest['source_reference']} version {manifest['version']}"


def main():
    if not MANIFEST_PATH.exists():
        print(f"FAIL: authoritative manifest missing: {MANIFEST_PATH}")
        return 1
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    required_manifest = {"status", "source_reference", "version", "processors"}
    missing = required_manifest - manifest.keys()
    if missing:
        print(f"FAIL: manifest missing fields {sorted(missing)}")
        return 1
    if manifest["status"] != "verified":
        print("FAIL: manifest status is not 'verified'; install the organizer-supplied manifest")
        return 1
    if not manifest["source_reference"] or not manifest["version"]:
        print("FAIL: manifest requires an authoritative source reference and version")
        return 1
    results = [validate_processor(name, path, manifest) for name, path in PROCESSORS.items()]
    for ok, message in results:
        print(message)
    return 0 if all(ok for ok, _ in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
