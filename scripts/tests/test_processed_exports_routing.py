"""Tests for processed_exports_routing and validate_13_month_window partial-tail behavior."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from processed_exports_routing import (
    archive_existing_destination,
    archive_prefix_from_filename,
    canonical_folder_for_mapping,
    prepare_destination_file,
    resolve_category_directory,
)
from validate_13_month_window import calculate_13_month_window_through, validate_file
from validate_response_time_exports import validate_response_time_csv


class TestArchivePrefix(unittest.TestCase):
    def test_yyyy_mm_prefix(self) -> None:
        self.assertEqual(archive_prefix_from_filename("2026_02_foo.csv"), "2026_02")

    def test_space_separator(self) -> None:
        self.assertEqual(archive_prefix_from_filename("2026 02_foo.csv"), "2026_02")

    def test_compact_prefix(self) -> None:
        self.assertEqual(archive_prefix_from_filename("202602_foo.csv"), "2026_02")

    def test_undated(self) -> None:
        self.assertEqual(archive_prefix_from_filename("foo.csv"), "undated")


class TestCanonicalFolders(unittest.TestCase):
    def test_legacy_aliases(self) -> None:
        self.assertEqual(canonical_folder_for_mapping("social_media_and_time_report"), "monthly_accrual_and_usage")
        self.assertEqual(canonical_folder_for_mapping("traffic_mva"), "traffic")
        self.assertEqual(canonical_folder_for_mapping("detectives_pt1"), "detectives")
        self.assertEqual(canonical_folder_for_mapping("social_media_posts"), "social_media")
        self.assertEqual(
            canonical_folder_for_mapping("monthly_accrual_and_usage_summary"),
            "monthly_accrual_and_usage",
        )


class TestResolveCategoryDirectory(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_prefers_existing_case(self) -> None:
        drone = self.tmp / "Drone"
        drone.mkdir()
        resolved = resolve_category_directory(self.tmp, "drone")
        self.assertEqual(resolved, drone)

    def test_legacy_social_media_time_report_folder_reused(self) -> None:
        old = self.tmp / "social_media_and_time_report"
        old.mkdir()
        resolved = resolve_category_directory(self.tmp, "monthly_accrual_and_usage")
        self.assertEqual(resolved, old)


class TestPrepareDestination(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_archives_then_free(self) -> None:
        dest = self.tmp / "out.csv"
        dest.write_text("v1\n", encoding="utf-8")
        src = self.tmp / "src.csv"
        src.write_text("v2\n", encoding="utf-8")
        logs: list[str] = []

        def _log(msg: str) -> None:
            logs.append(msg)

        r = prepare_destination_file(dest, src, dry_run=False, log=_log)
        self.assertIsNone(r)
        self.assertFalse(dest.exists())
        arch_dirs = list((self.tmp / "archive").rglob("*.csv"))
        self.assertEqual(len(arch_dirs), 1)

    def test_archive_under_category_uses_yyyy_mm_prefix(self) -> None:
        cat = self.tmp / "summons"
        cat.mkdir()
        dest = cat / "2026_01_department_wide_summons.csv"
        dest.write_text("old\n", encoding="utf-8")
        src = self.tmp / "src.csv"
        src.write_text("new\n", encoding="utf-8")
        r = prepare_destination_file(dest, src, dry_run=False, log=lambda *_a, **_k: None)
        self.assertIsNone(r)
        arc = cat / "archive" / "2026_01"
        self.assertTrue(any(arc.glob("*.csv")))

    def test_skip_archive_when_already_under_archive(self) -> None:
        arc = self.tmp / "summons" / "archive" / "2026_01"
        arc.mkdir(parents=True)
        dest = arc / "2026_01_foo.csv"
        dest.write_text("x\n", encoding="utf-8")
        moved = archive_existing_destination(dest, dry_run=False, log=lambda *_a, **_k: None)
        self.assertFalse(moved)
        self.assertTrue(dest.exists())


class TestValidateResponseTime(unittest.TestCase):
    def setUp(self) -> None:
        self._tdir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self._tdir, True)

    def _write(self, df: pd.DataFrame, name: str = "t.csv") -> Path:
        p = self._tdir / name
        df.to_csv(p, index=False)
        return p

    def test_priority_matrix_ok(self) -> None:
        df = pd.DataFrame(
            {
                "MM-YY": ["02-26"],
                "Response_Type": ["Emergency"],
                "Metric_Label": ["Total Response"],
                "RT Avg Formatted": ["6.5 min"],
            }
        )
        ok, _warns, errs = validate_response_time_csv(self._write(df))
        self.assertTrue(ok)
        self.assertFalse(errs)

    def test_unrecognized_emits_warning_not_error(self) -> None:
        df = pd.DataFrame({"Value": [1]})
        ok, warns, errs = validate_response_time_csv(self._write(df))
        self.assertTrue(ok)
        self.assertFalse(errs)
        self.assertTrue(any("Unrecognized" in w for w in warns))

    def test_all_metrics_shape(self) -> None:
        df = pd.DataFrame(
            {
                "MM-YY": ["02-26"],
                "Response_Type": ["Emergency"],
                "Metric_Type": ["First Response"],
                "Avg_Minutes": [5.1],
                "Record_Count": [10],
            }
        )
        ok, warns, errs = validate_response_time_csv(self._write(df, "2026_02_response_time_all_metrics.csv"))
        self.assertTrue(ok)
        self.assertFalse(errs)

    def test_priority_matrix_blank_mm_warns(self) -> None:
        df = pd.DataFrame(
            {
                "MM-YY": ["", ""],
                "Response_Type": ["A", "B"],
                "Metric_Label": ["x", "y"],
                "RT Avg Formatted": ["1 min", "2 min"],
            }
        )
        ok, warns, errs = validate_response_time_csv(self._write(df))
        self.assertTrue(ok)
        self.assertFalse(errs)
        self.assertTrue(any("non-blank" in w.lower() or "blank" in w.lower() for w in warns))

    def test_series_missing_value_column_errors(self) -> None:
        df = pd.DataFrame({"Date_Sort_Key": ["2026-01-01"]})
        ok, _w, errs = validate_response_time_csv(self._write(df))
        self.assertFalse(ok)
        self.assertTrue(any("value" in e.lower() for e in errs))


class TestPartialTailMarch(unittest.TestCase):
    def test_extra_future_period_warns(self) -> None:
        # 13 months ending 02-26 plus partial 03-26
        rows = []
        periods = calculate_13_month_window_through(2026, 2)[2] + ["03-26"]
        for p in periods:
            rows.append({"Period": p, "v": 1})
        df = pd.DataFrame(rows)
        tdir = Path(tempfile.mkdtemp())
        fp = tdir / "x.csv"
        df.to_csv(fp, index=False)
        self.addCleanup(shutil.rmtree, tdir, True)

        status, msg = validate_file(
            fp,
            period_column="Period",
            report_month="2026-02",
            allow_partial_tail=True,
        )
        self.assertEqual(status, "WARN")
        self.assertIn("Partial", msg)


class TestNormalizeWindowEndMarch2026(unittest.TestCase):
    def test_drops_partial_03_26_when_window_ends_feb_2026(self) -> None:
        from normalize_visual_export_for_backfill import enforce_13_month_window

        df = pd.DataFrame({"Period": ["02-26", "03-26"], "x": [1, 2]})
        out = enforce_13_month_window(df.copy(), "Period", window_end_ym=(2026, 2))
        self.assertNotIn("03-26", set(out["Period"].astype(str)))
        self.assertFalse(out.empty)


if __name__ == "__main__":
    unittest.main()
