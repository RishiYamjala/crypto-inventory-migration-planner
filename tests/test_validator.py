from pathlib import Path

import validate_processors


def test_pending_manifest_cannot_certify_current_processors():
    manifest = validate_processors.json.loads(
        Path("processors/challenge_kit_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["status"] == "pending"
    assert validate_processors.main() == 1
