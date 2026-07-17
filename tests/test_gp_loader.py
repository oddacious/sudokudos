"""Tests for GP loader name/nick normalisation and per-round merge logic."""

import polars as pl
import pytest

from shared.data.loaders.gp import manual_adjustements, merge_dfs_by_year


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _round_df(rows, round_num, year=2026):
    """Build a minimal per-round GP DataFrame.

    rows: list of (Name, Country, Nick, points)  — Nick may be None or "".
    """
    names, countries, nicks, points = zip(*rows)
    round_col = f"GP_t{round_num} rank. points"
    return pl.DataFrame({
        "#": [float(i + 1) for i in range(len(rows))],
        "Name": list(names),
        "Country": list(countries),
        "Nick": list(nicks),
        "Points": [float(p) for p in points],
        round_col: [float(p) for p in points],
        "year": [year] * len(rows),
        "round": [round_num] * len(rows),
        "source_file": [f"gp_results{year}_r{round_num}.csv"] * len(rows),
    })


def _pseudo_ids(df):
    return df.get_column("user_pseudo_id").to_list()


# ---------------------------------------------------------------------------
# manual_adjustements: name_to_name
# ---------------------------------------------------------------------------

class TestNameToName:
    def test_capitalisation_variant_normalised(self):
        """'Seonghwa Hong' (R5 capitalisation) should map to 'SeongHwa Hong'."""
        df = _round_df([("Seonghwa Hong", "Korea, South", "Pfaff", 500)], round_num=5)
        result = manual_adjustements(df)
        assert result["Name"].to_list() == ["SeongHwa Hong"]

    def test_unaffected_name_unchanged(self):
        df = _round_df([("Tantan Dai", "China", "TantanD", 900)], round_num=1)
        result = manual_adjustements(df)
        assert result["Name"].to_list() == ["Tantan Dai"]

    def test_dai_tantan_variant_normalised(self):
        """'Dai Tantan' (Last First format) should normalise to 'Tantan Dai'."""
        df = _round_df([("Dai Tantan", "China", "TantanD", 900)], round_num=1)
        result = manual_adjustements(df)
        assert result["Name"].to_list() == ["Tantan Dai"]


# ---------------------------------------------------------------------------
# manual_adjustements: name_to_nick
# ---------------------------------------------------------------------------

class TestNameToNick:
    def test_nick_assigned_when_blank(self):
        """'SeongHwa Hong' with blank Nick should get Nick='Pfaff'."""
        df = _round_df([("SeongHwa Hong", "Korea, South", "", 595)], round_num=1)
        result = manual_adjustements(df)
        assert result["Nick"].to_list() == ["Pfaff"]

    def test_nick_assigned_when_null(self):
        # Nick must be typed as String (not Null) to match what pl.read_csv produces.
        df = pl.DataFrame({
            "#": [1.0],
            "Name": ["SeongHwa Hong"],
            "Country": ["Korea, South"],
            "Nick": pl.Series([None], dtype=pl.String),
            "Points": [595.0],
            "GP_t1 rank. points": [595.0],
            "year": [2026],
            "round": [1],
            "source_file": ["gp_results2026_r1.csv"],
        })
        result = manual_adjustements(df)
        assert result["Nick"].to_list() == ["Pfaff"]

    def test_existing_nick_preserved_when_no_mapping(self):
        df = _round_df([("Tantan Dai", "China", "TantanD", 900)], round_num=1)
        result = manual_adjustements(df)
        assert result["Nick"].to_list() == ["TantanD"]

    def test_name_to_nick_overrides_existing_nick(self):
        """name_to_nick should apply even if a (wrong) nick is already present."""
        df = _round_df([("SeongHwa Hong", "Korea, South", "WrongNick", 595)], round_num=1)
        result = manual_adjustements(df)
        assert result["Nick"].to_list() == ["Pfaff"]


# ---------------------------------------------------------------------------
# manual_adjustements: nick_to_nick
# ---------------------------------------------------------------------------

class TestNickToNick:
    def test_alias_nick_collapsed(self):
        """'Qyz_' is a known alias for 'qyz' and should be normalised."""
        df = _round_df([("Some Solver", "Poland", "Qyz_", 700)], round_num=1)
        result = manual_adjustements(df)
        assert result["Nick"].to_list() == ["qyz"]


# ---------------------------------------------------------------------------
# merge_dfs_by_year: blank-nick split regression
# ---------------------------------------------------------------------------

class TestMergeDfsByYear:
    def test_blank_nick_round_merges_with_nick_rounds(self):
        """A solver appearing without their nick in one round (common when the GP
        site omits it) must still merge with rounds where the nick is present,
        producing a single row rather than splitting into two identities.

        Regression for: SeongHwa Hong appearing as (Nickless) in GP R1 2026
        while (Pfaff) in R2-R4, resulting in a split identity.
        """
        r1 = _round_df([("SeongHwa Hong", "Korea, South", "", 595)], round_num=1)
        r2 = _round_df([("SeongHwa Hong", "Korea, South", "Pfaff", 594)], round_num=2)

        all_dataframes = {2026: {1: r1, 2: r2}}
        merged = merge_dfs_by_year(all_dataframes)

        assert len(merged) == 1
        result = merged[0]
        assert result.shape[0] == 1, "Should be exactly one row for this solver"
        assert result["Nick"].to_list() == ["Pfaff"]

    def test_distinct_solvers_not_merged(self):
        """Two different solvers in the same round must remain separate rows."""
        r1 = _round_df([
            ("Alice Smith", "USA", "alice", 800),
            ("Bob Jones", "UK", "bob", 700),
        ], round_num=1)
        r2 = _round_df([
            ("Alice Smith", "USA", "alice", 850),
            ("Bob Jones", "UK", "bob", 650),
        ], round_num=2)

        all_dataframes = {2026: {1: r1, 2: r2}}
        merged = merge_dfs_by_year(all_dataframes)

        assert len(merged) == 1
        assert merged[0].shape[0] == 2

    def test_single_round_year_passthrough(self):
        """A year with only one round file should pass through unchanged."""
        r1 = _round_df([("Alice Smith", "USA", "alice", 800)], round_num=1)
        all_dataframes = {2025: {"[All]": r1}}
        merged = merge_dfs_by_year(all_dataframes)

        assert len(merged) == 1
        assert merged[0].shape[0] == 1

    def test_points_summed_across_rounds(self):
        """Total Points for a merged solver should equal the sum of their round scores."""
        r1 = _round_df([("Alice Smith", "USA", "alice", 800)], round_num=1)
        r2 = _round_df([("Alice Smith", "USA", "alice", 900)], round_num=2)

        all_dataframes = {2026: {1: r1, 2: r2}}
        merged = merge_dfs_by_year(all_dataframes)

        # merge_dfs_by_year casts Points back to String to match single-round files.
        assert merged[0]["Points"].to_list() == ["1700.0"]

    def test_points_top6_matches_points_when_six_or_fewer_rounds(self):
        """With <=6 rounds played, PointsTop6 should equal the full Points total."""
        r1 = _round_df([("Alice Smith", "USA", "alice", 800)], round_num=1)
        r2 = _round_df([("Alice Smith", "USA", "alice", 900)], round_num=2)

        all_dataframes = {2026: {1: r1, 2: r2}}
        merged = merge_dfs_by_year(all_dataframes)

        assert merged[0]["PointsTop6"].to_list() == ["1700.0"]

    def test_points_top6_drops_worst_round_beyond_six(self):
        """With 7 rounds played, Points sums all 7 but PointsTop6 drops the worst one."""
        round_scores = [800, 900, 700, 600, 500, 400, 100]
        rounds = {
            round_num: _round_df(
                [("Alice Smith", "USA", "alice", score)], round_num=round_num)
            for round_num, score in enumerate(round_scores, start=1)
        }

        all_dataframes = {2026: rounds}
        merged = merge_dfs_by_year(all_dataframes)

        assert merged[0]["Points"].to_list() == [str(float(sum(round_scores)))]
        assert merged[0]["PointsTop6"].to_list() == [str(float(sum(round_scores) - 100))]

    def test_points_top6_passthrough_for_single_file_year(self):
        """Single-file (aggregate-format) years should get PointsTop6 == Points."""
        r1 = _round_df([("Alice Smith", "USA", "alice", 800)], round_num=1)
        all_dataframes = {2025: {"[All]": r1}}
        merged = merge_dfs_by_year(all_dataframes)

        assert merged[0]["PointsTop6"].to_list() == merged[0]["Points"].to_list()
