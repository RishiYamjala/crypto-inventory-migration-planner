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


def test_scored_inventory_contains_explainable_priority_fields(tmp_path):
    df = score_inventory("data/raw/inventory.csv", tmp_path)
    assert len(df) == 10
    assert list(df["priority_rank"]) == list(range(1, 11))
    assert df["risk_rationale"].notna().all()
    assert (tmp_path / "migration_plan.csv").exists()
