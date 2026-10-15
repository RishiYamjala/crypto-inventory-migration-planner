import csv

import pytest

from scripts.evaluate_public_repo import _read_ground_truth, calculate_metrics


def test_metrics_include_false_positives_and_reviewed_missed_positives():
    detections = {("a.py", "RSA"), ("b.py", "ECDSA")}
    annotations = {
        ("a.py", "RSA"): True,
        ("b.py", "ECDSA"): False,
        ("c.py", "DH"): True,
    }
    result = calculate_metrics(detections, annotations)
    assert result["true_positives"] == 1
    assert result["false_positives"] == 1
    assert result["false_negatives"] == 1
    assert result["precision"] == pytest.approx(0.5)
    assert result["recall"] == pytest.approx(0.5)


def test_metrics_refuse_unreviewed_detection_pairs():
    with pytest.raises(ValueError, match="Every detected pair must be reviewed"):
        calculate_metrics({("a.py", "RSA")}, {})


def test_ground_truth_rejects_unreviewed_rows(tmp_path):
    path = tmp_path / "truth.csv"
    path.write_text(
        "path,algorithm,is_present,reviewed\na.py,RSA,true,false\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="not marked reviewed"):
        _read_ground_truth(path)


def test_ground_truth_rejects_duplicate_path_algorithm_pairs(tmp_path):
    path = tmp_path / "truth.csv"
    path.write_text(
        "path,algorithm,is_present,reviewed\na.py,RSA,true,true\na.py,RSA,false,true\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate ground-truth pair"):
        _read_ground_truth(path)
