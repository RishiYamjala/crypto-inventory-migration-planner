import pandas as pd

from src.problem import migration_for, score_inventory


def row(asset_name, algorithm, usage):
    return pd.Series({
        "asset_name": asset_name,
        "algorithm": algorithm,
        "usage": usage,
        "sensitivity": "High",
        "lifespan": "5-10 years",
    })


def test_key_exchange_does_not_use_signature_algorithm():
    recommendation, _ = migration_for(row("Employee VPN", "ECDH P-256", "VPN"))
    assert "ML-KEM" in recommendation
    assert "ML-DSA" not in recommendation


def test_signature_use_does_not_use_kem_alone():
    recommendation, _ = migration_for(row("Code Signing", "ECDSA P-256", "Code Signing"))
    assert "ML-DSA" in recommendation
    assert "ML-KEM" not in recommendation


def test_tls_certificate_covers_both_roles():
    recommendation, effort = migration_for(row("Customer Portal Certificate", "RSA-2048", "TLS/HTTPS"))
    assert "ML-KEM" in recommendation and "ML-DSA" in recommendation
    assert effort == "High"


def test_rsa_tls_role_review_does_not_depend_on_asset_name():
    from src.problem import algorithm_role

    for asset_name in ["Web Server", "Customer Portal", "TLS Certificate"]:
        item = row(asset_name, "RSA-2048", "TLS/HTTPS")
        recommendation, effort = migration_for(item)
        role = algorithm_role(item["algorithm"], item["usage"])
        assert "Review RSA role" in recommendation
        assert "ML-KEM" in recommendation and "ML-DSA" in recommendation
        assert effort == "High"
        assert "role review required" in role


def test_rsa_tls_does_not_return_no_action_for_non_certificate_name():
    recommendation, effort = migration_for(row("Web Server", "RSA-3072", "TLS/HTTPS"))
    assert recommendation != "No action"
    assert effort != "None"


def test_scored_inventory_contains_explainable_priority_fields(tmp_path):
    df = score_inventory("data/raw/inventory.csv", tmp_path)
    assert len(df) == 10
    assert list(df["priority_rank"]) == list(range(1, 11))
    assert df["risk_rationale"].notna().all()
    assert (tmp_path / "migration_plan.csv").exists()


def test_scanner_algorithm_labels_have_migration_recommendations():
    from src.problem import vulnerability_score

    assert vulnerability_score("ECC") > 0
    assert "ML-KEM" in migration_for(row("Key agreement", "ECDH", "VPN"))[0]
    assert "ML-DSA" in migration_for(row("Signer", "ECDSA", "Digital Signatures"))[0]
    assert "Confirm ECC role" in migration_for(row("Curve", "ECC", "Configuration Evidence"))[0]
    assert "Confirm RSA role" in migration_for(row("RSA asset", "RSA", "VPN"))[0]


def test_all_eight_requested_migration_fields_are_written(tmp_path):
    from src.problem import predicted_label

    df = score_inventory("data/raw/inventory.csv", tmp_path)
    required = {
        "asset_id", "predicted_label", "priority_score", "priority_rank",
        "recommended_action", "migration_wave", "depends_on", "rationale",
    }
    assert required.issubset(df.columns)
    plan = pd.read_csv(tmp_path / "migration_plan.csv")
    assert required.issubset(plan.columns)
    assert plan["asset_id"].is_unique
    assert plan["asset_id"].notna().all()
    assert plan["priority_score"].between(0, 100).all()
    assert plan["priority_rank"].tolist() == list(range(1, len(plan) + 1))
    assert plan["recommended_action"].notna().all()
    assert plan["migration_wave"].notna().all()
    assert plan["rationale"].notna().all()
    assert set(plan["predicted_label"]).issubset({
        "QUANTUM_VULNERABLE", "QUANTUM_RESISTANT", "HYBRID",
        "SYMMETRIC_OR_HASH", "LEGACY_BROKEN", "UNKNOWN",
    })


def test_predicted_label_taxonomy_covers_all_six_classes():
    from src.problem import predicted_label

    assert predicted_label("RSA-2048", "TLS/HTTPS", "") == "QUANTUM_VULNERABLE"
    assert predicted_label("Ed25519", "SSH", "") == "QUANTUM_VULNERABLE"
    assert predicted_label("ML-KEM", "KEM", "") == "QUANTUM_RESISTANT"
    assert predicted_label("HYBRID-KEM", "TLS/HTTPS", "") == "HYBRID"
    assert predicted_label("AES-256", "Encryption", "") == "SYMMETRIC_OR_HASH"
    assert predicted_label("SHA-1", "Hashing", "") == "LEGACY_BROKEN"
    assert predicted_label("UnlistedCipher", "Unknown", "") == "UNKNOWN"


def test_explicit_dependencies_are_preserved_and_missing_dependencies_are_empty(tmp_path):
    import csv

    source = tmp_path / "inventory_with_dependencies.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "asset_name", "algorithm", "usage", "sensitivity", "lifespan", "depends_on",
        ])
        writer.writeheader()
        writer.writerow({
            "asset_name": "API signer", "algorithm": "RSA-2048",
            "usage": "API Tokens/JWT", "sensitivity": "High",
            "lifespan": "5-10 years", "depends_on": "Identity Service;Key Vault",
        })
        writer.writerow({
            "asset_name": "Archive hash", "algorithm": "SHA-256",
            "usage": "Hashing", "sensitivity": "Low",
            "lifespan": "1-5 years", "depends_on": "",
        })
    df = score_inventory(source, tmp_path / "out").set_index("asset_name")
    assert df.loc["API signer", "depends_on"] == "Identity Service;Key Vault"
    assert df.loc["Archive hash", "depends_on"] == ""


def test_duplicate_asset_names_get_unique_deterministic_ids(tmp_path):
    import csv

    source = tmp_path / "duplicate_assets.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "asset_name", "algorithm", "usage", "sensitivity", "lifespan",
        ])
        writer.writeheader()
        for _ in range(2):
            writer.writerow({
                "asset_name": "Shared API", "algorithm": "RSA-2048",
                "usage": "API Tokens/JWT", "sensitivity": "High",
                "lifespan": "5-10 years",
            })
    df = score_inventory(source, tmp_path / "out")
    assert df["asset_id"].is_unique
    assert set(df["asset_id"]) == {"shared-api", "shared-api-2"}



def test_unknown_algorithm_is_not_silently_marked_safe(tmp_path):
    import csv

    source = tmp_path / "unknown_algorithm.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "asset_name", "algorithm", "usage", "sensitivity", "lifespan",
        ])
        writer.writeheader()
        writer.writerow({
            "asset_name": "Uncatalogued crypto", "algorithm": "MysteryCipher",
            "usage": "Unknown", "sensitivity": "High", "lifespan": "5-10 years",
        })
    df = score_inventory(source, tmp_path / "out")
    item = df.iloc[0]
    assert item["predicted_label"] == "UNKNOWN"
    assert item["risk_level"] == "Unknown"
    assert item["migration_wave"] == "Phase 1 (0-6 months)"
    assert "validate" in item["recommended_action"].lower()
    assert "not recognized" in item["rationale"].lower()
