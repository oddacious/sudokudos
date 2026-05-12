"""Tests for data manipulation functions — generalized for GP, WSC, and ESC."""

import polars as pl
import pytest

from shared.data.manipulation import (
    create_flat_dataset,
    merge_flat_datasets,
    merge_unflat_datasets,
    ids_by_total_points,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _gp_row(user_id, name, year, points, rank=1, r1=100.0, r2=50.0):
    return {
        "user_pseudo_id": user_id, "Name": name, "Country": "XX", "Nick": "nick",
        "year": year, "#": 1, "Played GPs": 1, "Total GPs": 1,
        "Rank_before_playoffs": rank, "Playoff_rank": None, "Rank": rank, "Points": float(points),
        "GP_t1 points": r1, "GP_t1 position": 1.0, "GP_t1 rank. points": r1,
        "GP_t2 points": r2, "GP_t2 position": 2.0, "GP_t2 rank. points": r2,
    }


def _wsc_row(user_id, name, year, total, official_rank=1):
    return {
        "user_pseudo_id": user_id, "Name": name, "year": year,
        "Official": True, "Official_rank": official_rank, "Unofficial_rank": official_rank,
        "WSC_total": float(total), "WSC_entry": True,
        "WSC_t1 points": float(total), "WSC_t1 position": 1.0,
    }


def _esc_row(user_id, name, year, total, esc_rank=1):
    return {
        "user_pseudo_id": user_id, "Name": name, "Country": "XX", "year": year,
        "ESC_rank": esc_rank, "ESC_unofficial_rank": esc_rank,
        "ESC_total": float(total),
        "ESC_t1 points": float(total), "ESC_t1 position": 1.0,
    }


def _df(rows):
    return pl.DataFrame(rows)


# ── create_flat_dataset ───────────────────────────────────────────────────────

class TestCreateFlatDataset:
    def test_gp_produces_year_round_columns(self):
        df = _df([_gp_row("id1", "Alice", 2024, 150)])
        flat = create_flat_dataset(df, metric="points", competition="GP")
        assert "2024_1" in flat.columns
        assert "2024_2" in flat.columns

    def test_wsc_produces_year_round_columns(self):
        df = _df([_wsc_row("id1", "Alice", 2024, 200)])
        flat = create_flat_dataset(df, metric="points", competition="WSC")
        assert "2024_1" in flat.columns

    def test_esc_produces_year_round_columns(self):
        rows = [{
            "user_pseudo_id": "id1", "Name": "Alice", "Country": "DE", "year": 2026,
            "ESC_rank": 1, "ESC_unofficial_rank": 1, "ESC_total": 300.0,
            "ESC_t1 points": 300.0,
        }]
        df = _df(rows)
        flat = create_flat_dataset(df, metric="points", competition="ESC")
        assert "2026_1" in flat.columns

    def test_esc_kept_columns_present(self):
        rows = [{
            "user_pseudo_id": "id1", "Name": "Alice", "Country": "DE", "year": 2026,
            "ESC_rank": 1, "ESC_unofficial_rank": 1, "ESC_total": 300.0,
            "ESC_t1 points": 300.0,
        }]
        flat = create_flat_dataset(_df(rows), competition="ESC")
        for col in ("ESC_rank", "ESC_unofficial_rank", "ESC_total", "user_pseudo_id", "Name"):
            assert col in flat.columns, f"Expected column {col} in flat ESC output"

    def test_unknown_competition_raises(self):
        df = _df([_gp_row("id1", "Alice", 2024, 100)])
        with pytest.raises(ValueError, match="unexpected competition"):
            create_flat_dataset(df, competition="UNKNOWN")


# ── merge_unflat_datasets ─────────────────────────────────────────────────────

class TestMergeUnflatDatasets:
    def _make_gp_df(self):
        return _df([_gp_row("id1", "Alice", 2024, 150), _gp_row("id2", "Bob", 2024, 100)])

    def _make_wsc_df(self):
        return _df([_wsc_row("id1", "Alice", 2024, 200)])

    def _make_esc_df(self):
        return _df([_esc_row("id1", "Alice", 2026, 300)])

    def test_baseline_no_extra_datasets(self):
        merged = merge_unflat_datasets(self._make_gp_df(), self._make_wsc_df())
        assert "WSC_total" in merged.columns
        assert not any(c.startswith("ESC_") for c in merged.columns)

    def test_extra_datasets_adds_esc_columns(self):
        merged = merge_unflat_datasets(
            self._make_gp_df(), self._make_wsc_df(),
            extra_datasets=[self._make_esc_df()])
        assert "ESC_total" in merged.columns
        assert "ESC_t1 points" in merged.columns

    def test_extra_datasets_position_columns_computed(self):
        merged = merge_unflat_datasets(
            self._make_gp_df(), self._make_wsc_df(),
            extra_datasets=[self._make_esc_df()])
        assert "ESC_t1 position" in merged.columns

    def test_extra_datasets_left_join_preserves_gp_rows(self):
        # Bob has no ESC entry; his row should still be present with null ESC columns
        merged = merge_unflat_datasets(
            self._make_gp_df(), self._make_wsc_df(),
            extra_datasets=[self._make_esc_df()])
        bob = merged.filter(pl.col("user_pseudo_id") == "id2")
        assert len(bob) > 0
        assert bob["ESC_total"].is_null().all()

    def test_extra_datasets_none_is_backward_compatible(self):
        merged_default = merge_unflat_datasets(self._make_gp_df(), self._make_wsc_df())
        merged_explicit = merge_unflat_datasets(
            self._make_gp_df(), self._make_wsc_df(), extra_datasets=None)
        assert set(merged_default.columns) == set(merged_explicit.columns)


# ── merge_flat_datasets ───────────────────────────────────────────────────────

class TestMergeFlatDatasets:
    def _flat(self, user_id, name, suffix_col, value):
        return pl.DataFrame({
            "user_pseudo_id": [user_id],
            "Name": [name],
            "2026_1": [value],
        })

    def test_two_datasets(self):
        a = self._flat("id1", "Alice", "_gp", 100.0)
        b = self._flat("id1", "Alice", "_wsc", 200.0)
        merged = merge_flat_datasets([a, b], ("_gp", "_wsc"))
        assert "2026_1_gp" in merged.columns
        assert "2026_1_wsc" in merged.columns

    def test_three_datasets(self):
        a = self._flat("id1", "Alice", "_gp", 100.0)
        b = self._flat("id1", "Alice", "_wsc", 200.0)
        c = self._flat("id1", "Alice", "_esc", 300.0)
        merged = merge_flat_datasets([a, b, c], ("_gp", "_wsc", "_esc"))
        assert "2026_1_gp" in merged.columns
        assert "2026_1_wsc" in merged.columns
        assert "2026_1_esc" in merged.columns

    def test_mismatched_lengths_raises(self):
        a = self._flat("id1", "Alice", "_gp", 100.0)
        b = self._flat("id1", "Alice", "_wsc", 200.0)
        with pytest.raises(ValueError):
            merge_flat_datasets([a, b], ("_gp",))


# ── ids_by_total_points ───────────────────────────────────────────────────────

class TestIdsByTotalPoints:
    def test_includes_esc_total(self):
        rows = [
            {"user_pseudo_id": "id1", "Name": "Alice", "year": 2026,
             "Points": 100.0, "WSC_total": 0.0, "ESC_total": 500.0},
            {"user_pseudo_id": "id2", "Name": "Bob", "year": 2026,
             "Points": 800.0, "WSC_total": 0.0, "ESC_total": None},
        ]
        df = pl.DataFrame(rows)
        ordered = ids_by_total_points(df)
        # Bob has 800 GP, Alice has 600 (100 GP + 500 ESC)
        assert ordered[0] == "id2"
        assert ordered[1] == "id1"

    def test_no_esc_column_still_works(self):
        rows = [
            {"user_pseudo_id": "id1", "Name": "Alice", "year": 2024,
             "Points": 100.0, "WSC_total": 200.0},
            {"user_pseudo_id": "id2", "Name": "Bob", "year": 2024,
             "Points": 400.0, "WSC_total": 0.0},
        ]
        df = pl.DataFrame(rows)
        ordered = ids_by_total_points(df)
        # Bob: 400 GP, Alice: 300 (100 GP + 200 WSC) → Bob first
        assert ordered[0] == "id2"
        assert ordered[1] == "id1"

    def test_ordering_is_descending(self):
        rows = [
            {"user_pseudo_id": f"id{i}", "Name": f"Solver{i}", "year": 2024,
             "Points": float(i * 10), "WSC_total": 0.0, "ESC_total": 0.0}
            for i in range(1, 5)
        ]
        df = pl.DataFrame(rows)
        ordered = ids_by_total_points(df)
        points = [int(s[2:]) * 10 for s in ordered]
        assert points == sorted(points, reverse=True)
