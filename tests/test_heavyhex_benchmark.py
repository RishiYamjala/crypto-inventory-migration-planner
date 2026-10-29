import pandas as pd
import pytest

from src.heavyhex_benchmark import (
    COMPARISON_OUTPUT,
    PROCESSOR_PATHS,
    STRESS_OUTPUT,
    run_heavyhex_comparison,
    run_heavyhex_stress_test,
)
from src.metrics import SEED, SHOTS

LABELS = list(PROCESSOR_PATHS)
HEAVY_HEX_LABELS = ["Processor B heavy-hex 7q", "Processor B heavy-hex 9q"]


@pytest.fixture(scope="module")
def comparison():
    return run_heavyhex_comparison()


@pytest.fixture(scope="module")
def stress():
    return run_heavyhex_stress_test()


def test_comparison_covers_all_four_processors_with_shared_settings(comparison):
    assert list(comparison["label"]) == LABELS
    assert set(comparison["shots"]) == {SHOTS}
    assert set(comparison["seed"]) == {SEED}
    # The ideal (noise-free) reference must not depend on the processor.
    assert comparison["ideal_success_probability"].nunique() == 1
    assert (comparison["extra_two_qubit_gates"] >= 0).all()


def test_heavy_hex_variants_have_no_triangles_and_are_never_cheaper_than_phase1_b(comparison):
    by_label = comparison.set_index("label")
    phase1_b = by_label.loc["Processor B"]
    assert phase1_b["triangles"] == 2
    for label in HEAVY_HEX_LABELS:
        row = by_label.loc[label]
        assert row["triangles"] == 0
        assert row["two_qubit_gates"] >= phase1_b["two_qubit_gates"]
        assert row["depth"] >= phase1_b["depth"]


def test_stress_test_has_every_workload_on_every_processor(stress):
    assert len(stress) == 3 * len(LABELS)
    for workload, group in stress.groupby("workload"):
        assert list(group["label"]) == LABELS, workload
    assert (stress["extra_two_qubit_gates"] >= 0).all()


def _assert_matches_committed(fresh, path, drop=()):
    committed = pd.read_csv(path)
    columns = [c for c in fresh.columns if c not in drop]
    pd.testing.assert_frame_equal(
        fresh[columns].reset_index(drop=True),
        committed[columns].reset_index(drop=True),
        check_dtype=False,
        check_exact=False,
        rtol=1e-9,
    )


def test_committed_comparison_csv_is_current(comparison):
    # runtime_seconds is wall-clock time and legitimately differs between runs.
    _assert_matches_committed(comparison, COMPARISON_OUTPUT, drop=("runtime_seconds",))


def test_committed_stress_csv_is_current(stress):
    _assert_matches_committed(stress, STRESS_OUTPUT)
