"""Tests for the European Sudoku Championship data loader."""

import os
import tempfile

import polars as pl
import pytest

from shared.data.loaders.eurosudoku import load_eurosudoku, COUNTRY_TYPO_MAP


REAL_CSV_DIR = "data/raw/eurosudoku"
EXPECTED_ROUND_COLS = [f"ESC_t{i} points" for i in range(1, 8)]
EXPECTED_SCHEMA_COLS = (
    ["Name", "Country", "year", "ESC_rank", "ESC_unofficial_rank", "ESC_total"]
    + EXPECTED_ROUND_COLS
)


def _write_csv(directory, filename, content):
    path = os.path.join(directory, filename)
    with open(path, "w") as f:
        f.write(content)
    return path


MINIMAL_CSV = """\
Rank,Unofficial,Country,Name,Team,Age,Newcomer,Sum,R1,R2,R3,R4,R5,R6,R7
1,1,Estonia,Tiit Vunk,EST-A,,,3350,375,325,740,620,420,480,390
,2,China,Tantan Dai,UN2,,,3340,310,300,710,660,680,270,410
"""


class TestSchema:
    def test_expected_columns_present(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_csv(tmpdir, "eurosudoku_2026.csv", MINIMAL_CSV)
            df = load_eurosudoku(tmpdir)
        assert set(EXPECTED_SCHEMA_COLS).issubset(set(df.columns))

    def test_year_column_is_int64(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_csv(tmpdir, "eurosudoku_2026.csv", MINIMAL_CSV)
            df = load_eurosudoku(tmpdir)
        assert df["year"].dtype == pl.Int64

    def test_esc_rank_is_nullable_int64(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_csv(tmpdir, "eurosudoku_2026.csv", MINIMAL_CSV)
            df = load_eurosudoku(tmpdir)
        assert df["ESC_rank"].dtype == pl.Int64
        # Second row should be null (unofficial)
        assert df["ESC_rank"][1] is None

    def test_round_columns_are_float64(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_csv(tmpdir, "eurosudoku_2026.csv", MINIMAL_CSV)
            df = load_eurosudoku(tmpdir)
        for col in EXPECTED_ROUND_COLS:
            assert df[col].dtype == pl.Float64, f"{col} should be Float64"

    def test_no_null_names(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_csv(tmpdir, "eurosudoku_2026.csv", MINIMAL_CSV)
            df = load_eurosudoku(tmpdir)
        assert df["Name"].is_null().sum() == 0


class TestYearExtraction:
    def test_year_extracted_from_filename(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_csv(tmpdir, "eurosudoku_2026.csv", MINIMAL_CSV)
            df = load_eurosudoku(tmpdir)
        assert df["year"].unique().to_list() == [2026]

    def test_non_matching_files_ignored(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_csv(tmpdir, "eurosudoku_2026.csv", MINIMAL_CSV)
            _write_csv(tmpdir, "readme.txt", "ignore me")
            _write_csv(tmpdir, "bad_name.csv", MINIMAL_CSV)
            df = load_eurosudoku(tmpdir)
        assert len(df) == 2  # only the valid file

    def test_multiple_years_concatenated(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_csv(tmpdir, "eurosudoku_2025.csv", MINIMAL_CSV)
            _write_csv(tmpdir, "eurosudoku_2026.csv", MINIMAL_CSV)
            df = load_eurosudoku(tmpdir)
        years = sorted(df["year"].unique().to_list())
        assert years == [2025, 2026]
        assert len(df) == 4  # 2 rows × 2 years

    def test_missing_directory_raises(self):
        with pytest.raises(FileNotFoundError):
            load_eurosudoku("/nonexistent/path")


class TestCountryNormalisation:
    def test_typos_are_fixed(self):
        typo_csv = """\
Rank,Unofficial,Country,Name,Team,Age,Newcomer,Sum,R1,R2,R3,R4,R5,R6,R7
1,1,Hungargy,Player A,HUN-A,,,100,10,10,10,10,10,10,40
,2,Hungaria,Player B,HUN-D,,,90,10,10,10,10,10,10,30
,3,Slovaka,Player C,SVK-D,,,80,10,10,10,10,10,10,20
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_csv(tmpdir, "eurosudoku_2026.csv", typo_csv)
            df = load_eurosudoku(tmpdir)
        countries = df["Country"].to_list()
        assert "Hungary" in countries
        assert "Slovakia" in countries
        assert "Hungargy" not in countries
        assert "Hungaria" not in countries
        assert "Slovaka" not in countries

    def test_typo_map_completeness(self):
        """All known CSV typos should be in COUNTRY_TYPO_MAP."""
        known_typos = {"Hungargy", "Hungaria", "Slovaka"}
        assert known_typos.issubset(set(COUNTRY_TYPO_MAP.keys()))


class TestRealData:
    """Smoke tests against the actual 2026 CSV (skipped if not present)."""

    @pytest.fixture
    def esc_2026(self):
        if not os.path.isdir(REAL_CSV_DIR):
            pytest.skip("Real ESC data not available")
        return load_eurosudoku(REAL_CSV_DIR)

    def test_row_count_2026(self, esc_2026):
        assert len(esc_2026) == 154

    def test_all_expected_columns(self, esc_2026):
        assert set(EXPECTED_SCHEMA_COLS).issubset(set(esc_2026.columns))

    def test_top_ranked_solver_2026(self, esc_2026):
        top = esc_2026.filter(pl.col("ESC_rank") == 1)
        assert len(top) == 1
        assert top["Name"][0] == "Tiit Vunk"
