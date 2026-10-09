import pandas as pd

from src.problem import algorithm_role, migration_for, score_inventory


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


def test_rsa_tls_certificate_recommends_signature_migration_and_separate_key_exchange_review():
    recommendation, effort = migration_for(row("Customer Portal Certificate", "RSA-2048", "TLS/HTTPS"))
    assert "ML-DSA" in recommendation
    assert "assess ML-KEM separately" in recommendation
    assert effort == "High"


def test_ecdsa_tls_certificate_is_not_missed():
    recommendation, effort = migration_for(row("Customer Portal Certificate", "ECDSA P-256", "TLS/HTTPS"))
    assert "ML-DSA" in recommendation
    assert "ML-KEM" in recommendation
    assert effort == "High"


def test_tls_certificate_role_is_not_mislabeled_as_key_exchange():
    assert algorithm_role("ECDSA P-256", "TLS/HTTPS", "Customer Portal Certificate") == "Certificate digital signature"
    assert algorithm_role("ECDH P-256", "TLS/HTTPS", "TLS key agreement config") == "Key establishment / key exchange"


def test_scored_inventory_contains_explainable_priority_fields(tmp_path):
    df = score_inventory("data/raw/inventory.csv", tmp_path)
    assert len(df) == 10
    assert list(df["priority_rank"]) == list(range(1, 11))
    assert df["risk_rationale"].notna().all()
    assert (tmp_path / "migration_plan.csv").exists()
