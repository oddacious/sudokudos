"""Tests for the name mapping algorithm in attempted_mapping."""

import polars as pl
import pytest

from shared.data.manipulation import attempted_mapping


def _make_gp(rows):
    """Build a minimal GP DataFrame with the columns needed by attempted_mapping."""
    return pl.DataFrame({
        "Name": [r[0] for r in rows],
        "Country": [r[1] for r in rows],
        "Nick": [r[2] for r in rows],
        "user_pseudo_id": [r[3] for r in rows],
        "year": [2024] * len(rows),
        "Points": [100.0] * len(rows),
        "Rank": [1] * len(rows),
        "Rank_before_playoffs": [1] * len(rows),
        "Playoff_rank": [None] * len(rows),
        "#": [1] * len(rows),
        "Played GPs": [1] * len(rows),
        "Total GPs": [1] * len(rows),
    })


def _make_other(names, countries=None):
    """Build a minimal other-competition DataFrame."""
    if countries is None:
        countries = ["Unknown"] * len(names)
    return pl.DataFrame({"Name": names, "Country": countries, "year": [2024] * len(names)})


def _get_ids(mapped_df):
    return mapped_df.get_column("user_pseudo_id").to_list()


class TestDirectNameMatch:
    def test_exact_match(self):
        gp = _make_gp([("Alice Smith", "USA", "alice", "Alice Smith (alice) - USA")])
        other = _make_other(["Alice Smith"])
        mapped = attempted_mapping(other, gp)
        assert _get_ids(mapped) == ["Alice Smith (alice) - USA"]

    def test_titlecase_normalisation(self):
        gp = _make_gp([("Alice Smith", "USA", "alice", "Alice Smith (alice) - USA")])
        other = _make_other(["alice smith"])
        mapped = attempted_mapping(other, gp)
        assert _get_ids(mapped) == ["Alice Smith (alice) - USA"]


class TestFlippedNameMatch:
    def test_last_first_format(self):
        """'Smith Alice' should match GP entry for 'Alice Smith'."""
        gp = _make_gp([("Alice Smith", "USA", "alice", "Alice Smith (alice) - USA")])
        other = _make_other(["Smith Alice"])
        mapped = attempted_mapping(other, gp)
        assert _get_ids(mapped) == ["Alice Smith (alice) - USA"]

    def test_comma_stripped_before_flip(self):
        gp = _make_gp([("Alice Smith", "USA", "alice", "Alice Smith (alice) - USA")])
        other = _make_other(["Smith, Alice"])
        mapped = attempted_mapping(other, gp)
        assert _get_ids(mapped) == ["Alice Smith (alice) - USA"]


class TestLowercaseMatch:
    def test_case_insensitive(self):
        gp = _make_gp([("Alice Smith", "USA", "alice", "Alice Smith (alice) - USA")])
        other = _make_other(["ALICE SMITH"])
        mapped = attempted_mapping(other, gp)
        assert _get_ids(mapped) == ["Alice Smith (alice) - USA"]


class TestManualOverride:
    def test_override_beats_auto_match(self):
        """If an override is supplied it should take precedence over any auto-match."""
        gp = _make_gp([("Bob Jones", "UK", "bob", "Bob Jones (bob) - UK")])
        other = _make_other(["Bob Jones"])
        override = {"Bob Jones": "OVERRIDDEN_ID"}
        mapped = attempted_mapping(other, gp, manual_override=override)
        assert _get_ids(mapped) == ["OVERRIDDEN_ID"]

    def test_override_flipped_name(self):
        """Override should also apply to flipped-name variants."""
        # Use a non-empty GP so the Name column schema is String, not Null
        gp = _make_gp([("Unrelated Person", "DE", "up", "Unrelated Person (up) - DE")])
        other = _make_other(["Alice Smith"])
        override = {"Smith Alice": "OVERRIDE_VIA_FLIP"}
        mapped = attempted_mapping(other, gp, manual_override=override)
        assert _get_ids(mapped) == ["OVERRIDE_VIA_FLIP"]

    def test_default_override_is_wsc_map(self):
        """When no override is passed, WSC_NAME_TO_GP_ID_OVERRIDE is applied."""
        from shared.competitions import WSC_NAME_TO_GP_ID_OVERRIDE
        assert len(WSC_NAME_TO_GP_ID_OVERRIDE) > 0  # sanity check

    def test_empty_override_disables_manual_mappings(self):
        gp = _make_gp([("Unrelated Person", "DE", "up", "Unrelated Person (up) - DE")])
        other = _make_other(["Zvěřina Jan"])
        mapped = attempted_mapping(other, gp, manual_override={})
        # Without override, falls back to name itself
        assert _get_ids(mapped) == ["Zvěřina Jan"]


class TestFallback:
    def test_unmatched_name_becomes_own_id(self):
        gp = _make_gp([("Someone Else", "DE", "nick", "Someone Else (nick) - DE")])
        other = _make_other(["Unknown Person"])
        mapped = attempted_mapping(other, gp)
        assert _get_ids(mapped) == ["Unknown Person"]

    def test_no_duplicate_rows_on_unique_gp_names(self):
        gp = _make_gp([
            ("Alice Smith", "USA", "alice", "Alice Smith (alice) - USA"),
            ("Bob Jones", "UK", "bob", "Bob Jones (bob) - UK"),
        ])
        other = _make_other(["Alice Smith", "Unknown"])
        mapped = attempted_mapping(other, gp)
        assert len(mapped) == 2

    def test_duplicate_gp_name_does_not_fan_out(self):
        """When the GP index has two entries for the same name, the result must not fan out."""
        gp = _make_gp([
            ("Alice Smith", "USA", "alice1", "Alice Smith (alice1) - USA"),
            ("Alice Smith", "USA", "alice2", "Alice Smith (alice2) - USA"),
        ])
        other = _make_other(["Alice Smith"])
        mapped = attempted_mapping(other, gp)
        assert len(mapped) == 1
