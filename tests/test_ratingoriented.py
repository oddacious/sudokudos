"""Tests for _compute_rating_ranks in shared/plots/ratingoriented.py."""

import polars as pl
import pytest

from shared.plots.ratingoriented import _compute_rating_ranks


def make_ts(*rows):
    """Build a minimal timeseries DataFrame from tuples.

    Accepts (user_pseudo_id, comp_idx, rating) or (user_pseudo_id, comp_idx, rating, year).
    Year defaults to 1 for all rows when omitted, keeping all solvers active in every test.
    """
    uids, idxs, ratings, years = [], [], [], []
    for row in rows:
        uids.append(row[0])
        idxs.append(row[1])
        ratings.append(float(row[2]))
        years.append(row[3] if len(row) > 3 else 1)
    return pl.DataFrame({
        "user_pseudo_id": uids,
        "comp_idx": idxs,
        "rating": ratings,
        "year": years,
    })


# ---------------------------------------------------------------------------
# Basic correctness
# ---------------------------------------------------------------------------

def test_rank_1_when_highest():
    """Solver with the highest rating at a point in time should be rank 1."""
    ts = make_ts(("A", 1, 1000), ("B", 1, 900), ("C", 1, 800))
    result = _compute_rating_ranks(ts, ["A"], {1})
    assert result[("A", 1)] == 1


def test_rank_reflects_position():
    """Rank should equal number of solvers with strictly higher rating plus one."""
    ts = make_ts(("A", 1, 800), ("B", 1, 900), ("C", 1, 1000))
    result = _compute_rating_ranks(ts, ["A", "B", "C"], {1})
    assert result[("C", 1)] == 1
    assert result[("B", 1)] == 2
    assert result[("A", 1)] == 3


# ---------------------------------------------------------------------------
# Historical carry-forward: earlier competitors still count later
# ---------------------------------------------------------------------------

def test_earlier_solver_counted_in_later_snapshot():
    """A solver who only competed at comp_idx 1 should still appear in the
    snapshot at comp_idx 2, keeping their last known rating."""
    ts = make_ts(
        ("A", 1, 1000),   # only round for A
        ("B", 2, 900),    # B starts at comp_idx 2
    )
    # At comp_idx 2: A's current rating is 1000, B's is 900 → B should be rank 2
    result = _compute_rating_ranks(ts, ["B"], {2})
    assert result[("B", 2)] == 2


def test_earlier_solver_not_counted_before_they_appear():
    """A solver's rating should not appear in snapshots before their first entry."""
    ts = make_ts(
        ("A", 2, 1000),   # A only starts at comp_idx 2
        ("B", 1, 900),
    )
    # At comp_idx 1: only B has been seen → B should be rank 1
    result = _compute_rating_ranks(ts, ["B"], {1})
    assert result[("B", 1)] == 1


# ---------------------------------------------------------------------------
# Multiple appearances: only most recent rating counts
# ---------------------------------------------------------------------------

def test_most_recent_rating_used():
    """Only the solver's most recent rating contributes to the snapshot.

    A has a low early rating (500) that is later replaced by a high one (1000).
    At comp_idx 3, A's snapshot rating should be 1000, placing them rank 1
    above B (600). If the old rating 500 were used, A would incorrectly be rank 2.
    """
    ts = make_ts(
        ("A", 1, 500),    # A: low early rating
        ("B", 2, 600),    # B: medium rating
        ("A", 3, 1000),   # A: improves
    )
    result = _compute_rating_ranks(ts, ["A"], {3})
    assert result[("A", 3)] == 1


def test_old_rating_superseded():
    """A solver's high early rating should be superseded by a lower later one.

    A starts at 1000 but drops to 500. At comp_idx 3, B(900) > A(500),
    so A should be rank 2. If the old rating 1000 were still used, A would
    incorrectly be rank 1.
    """
    ts = make_ts(
        ("A", 1, 1000),   # A: high early rating
        ("B", 2, 900),    # B joins
        ("A", 3, 500),    # A drops
    )
    result = _compute_rating_ranks(ts, ["A"], {3})
    assert result[("A", 3)] == 2


# ---------------------------------------------------------------------------
# Missing target: solver didn't compete at that comp_idx
# ---------------------------------------------------------------------------

def test_absent_at_target_not_in_results():
    """If a solver didn't participate at a target comp_idx, they should be absent."""
    ts = make_ts(("A", 1, 1000), ("B", 2, 900))
    result = _compute_rating_ranks(ts, ["A"], {2})
    assert ("A", 2) not in result


def test_absent_target_does_not_crash():
    """No error when none of the selected solvers competed at the target."""
    ts = make_ts(("A", 1, 1000), ("B", 2, 900))
    result = _compute_rating_ranks(ts, ["A"], {2})
    assert result == {}


# ---------------------------------------------------------------------------
# Tied ratings
# ---------------------------------------------------------------------------

def test_tied_ratings_same_rank():
    """Two solvers with equal ratings should receive the same rank."""
    ts = make_ts(("A", 1, 900), ("B", 1, 900), ("C", 1, 800))
    result = _compute_rating_ranks(ts, ["A", "B"], {1})
    assert result[("A", 1)] == result[("B", 1)]


def test_tied_ratings_rank_value():
    """With a tie at the top, both tied solvers should be rank 1 (no one above them)."""
    ts = make_ts(("A", 1, 900), ("B", 1, 900))
    result = _compute_rating_ranks(ts, ["A", "B"], {1})
    assert result[("A", 1)] == 1
    assert result[("B", 1)] == 1


# ---------------------------------------------------------------------------
# Multiple target comp_idxs in one call
# ---------------------------------------------------------------------------

def test_multiple_targets():
    """Results for multiple target comp_idxs are all returned in one call."""
    ts = make_ts(
        ("A", 1, 800),
        ("A", 2, 1000),
        ("B", 1, 900),
    )
    result = _compute_rating_ranks(ts, ["A"], {1, 2})
    assert result[("A", 1)] == 2   # B(900) > A(800) at comp_idx 1
    assert result[("A", 2)] == 1   # A(1000) > B(900) at comp_idx 2


# ---------------------------------------------------------------------------
# Active-leaderboard filtering: solvers inactive for > 1 year excluded
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Leaderboard consistency: at the most recent point, rank must match the
# leaderboard ordering (active solvers sorted by rating descending).
# Note: historical rank consistency is not tested here.
# ---------------------------------------------------------------------------

def test_final_point_rank_matches_leaderboard_ordering():
    """At the most recent comp_idx, ranks should equal position in rating-descending
    order among active solvers — consistent with leaderboard calculation.

    This would have caught the bug where inactive solvers inflated chart ranks
    beyond their leaderboard ranks.
    """
    ts = make_ts(
        ("A", 3, 1000, 2024),  # active, rank 1
        ("B", 3,  800, 2024),  # active, rank 2
        ("C", 3,  600, 2024),  # active, rank 3
        ("D", 1,  900, 2022),  # inactive: last year 2022 < 2024-1=2023
    )
    # D is excluded; ranks are among A, B, C only
    result = _compute_rating_ranks(ts, ["A", "B", "C"], {3})
    assert result[("A", 3)] == 1
    assert result[("B", 3)] == 2
    assert result[("C", 3)] == 3


def test_inactive_solver_excluded_from_rank():
    """A solver last active 2+ years ago should not count in the ranking."""
    ts = make_ts(
        ("A", 1, 1000, 2020),  # A last competed in 2020
        ("B", 2, 900,  2022),  # B competing in 2022
    )
    # At comp_idx 2 (year 2022): A's last year 2020 < 2022-1=2021, so inactive.
    # Only B is active → B is rank 1.
    result = _compute_rating_ranks(ts, ["B"], {2})
    assert result[("B", 2)] == 1


def test_solver_active_within_one_year_still_counts():
    """A solver last active exactly 1 year ago should still count."""
    ts = make_ts(
        ("A", 1, 1000, 2021),  # A last competed in 2021
        ("B", 2, 900,  2022),  # B competing in 2022
    )
    # At comp_idx 2 (year 2022): A's last year 2021 >= 2022-1=2021, so active.
    # A(1000) > B(900) → B is rank 2.
    result = _compute_rating_ranks(ts, ["B"], {2})
    assert result[("B", 2)] == 2
