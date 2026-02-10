"""
Run All ETL Verifications

Master script to run all ETL verifications and generate comprehensive summary.

Version: 1.0.0
Created: 2026-01-13
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import json

# Add verifications directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import verifiers
from overtime_timeoff_verifier import OvertimeTimeOffVerifier
from arrests_verifier import ArrestsVerifier


class VerificationRunner:
    """Master runner for all ETL verifications."""

    def __init__(self, current_month: str = "2025_12", backfill_month: str = "2025_11"):
        """
        Initialize verification runner.

        Args:
            current_month: Month to verify (default: "2025_12")
            backfill_month: Baseline month for comparison (default: "2025_11")
        """
        self.current_month = current_month
        self.backfill_month = backfill_month
        self.results = []
        self.start_time = datetime.now()

    def run_all_verifications(self) -> Dict:
        """
        Run all ETL verifications sequentially.

        Returns:
            Dictionary with overall results
        """
        print("=" * 80)
        print("MASTER AUTOMATION ETL VERIFICATION SUITE")
        print("=" * 80)
        print(f"Current Month: {self.current_month}")
        print(f"Backfill Month: {self.backfill_month}")
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()

        # Priority 1: Overtime & Time Off
        self._run_verification(
            name="Overtime & Time Off",
            verifier_class=OvertimeTimeOffVerifier,
            priority=1
        )

        # Priority 2: Arrests
        self._run_verification(
            name="Arrests",
            verifier_class=ArrestsVerifier,
            priority=2
        )

        # Generate summary
        return self._generate_summary()

    def _run_verification(self, name: str, verifier_class, priority: int):
        """
        Run a single verification.

        Args:
            name: Verification name
            verifier_class: Verifier class to instantiate
            priority: Priority level
        """
        print()
        print("-" * 80)
        print(f"[{priority}] RUNNING: {name}")
        print("-" * 80)

        result = {
            "name": name,
            "priority": priority,
            "start_time": datetime.now(),
            "status": "UNKNOWN",
            "pass_rate": 0.0,
            "issues": [],
            "report_path": None
        }

        try:
            # Initialize verifier
            verifier = verifier_class(
                current_month=self.current_month,
                backfill_month=self.backfill_month
            )

            # Check if output files exist
            print(f"[PRE-CHECK] Verifying {self.current_month} exports exist...")
            missing_files = []
            for filename in verifier.output_files:
                filepath = verifier.outputs_dir / filename
                if not filepath.exists():
                    # Try with month prefix
                    prefixed = f"{self.current_month}_{filename}"
                    filepath_prefixed = verifier.outputs_dir / prefixed
                    if not filepath_prefixed.exists():
                        missing_files.append(filename)
                        print(f"  [MISSING] {filename}")
                    else:
                        print(f"  [FOUND] {prefixed}")
                else:
                    print(f"  [FOUND] {filename}")

            if missing_files:
                result["status"] = "SKIPPED"
                result["issues"] = [f"Missing export files: {', '.join(missing_files)}"]
                print()
                print(f"[RESULT] {name}: SKIPPED - Missing export files")
            else:
                # Run verification
                print()
                print(f"[VERIFICATION] Running {name} verification...")
                verification_results = verifier.run_verification()

                result["status"] = verification_results["status"]
                result["pass_rate"] = verification_results.get("pass_rate", 0.0)
                result["issues"] = verification_results.get("issues", [])
                result["report_path"] = verification_results.get("report_path")

                print()
                print(f"[RESULT] {name}: {result['status']}")
                print(f"  Pass Rate: {result['pass_rate']:.1f}%")
                if result["report_path"]:
                    print(f"  Report: {result['report_path']}")

        except Exception as e:
            result["status"] = "ERROR"
            result["issues"] = [str(e)]
            print()
            print(f"[ERROR] {name}: {str(e)}")

        result["end_time"] = datetime.now()
        result["duration"] = (result["end_time"] - result["start_time"]).total_seconds()

        self.results.append(result)

    def _generate_summary(self) -> Dict:
        """
        Generate overall verification summary.

        Returns:
            Summary dictionary
        """
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        # Calculate statistics
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASSED")
        failed = sum(1 for r in self.results if r["status"] == "FAILED")
        skipped = sum(1 for r in self.results if r["status"] == "SKIPPED")
        errors = sum(1 for r in self.results if r["status"] == "ERROR")

        overall_pass_rate = (passed / total * 100) if total > 0 else 0.0

        summary = {
            "current_month": self.current_month,
            "backfill_month": self.backfill_month,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "total_verifications": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "overall_pass_rate": overall_pass_rate,
            "verifications": self.results
        }

        return summary

    def write_summary_report(self, summary: Dict):
        """
        Write summary report to file.

        Args:
            summary: Summary dictionary
        """
        report_dir = Path(__file__).parent.parent
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Write JSON
        json_path = report_dir / f"VERIFICATION_SUMMARY_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        # Write Markdown
        md_path = report_dir / f"VERIFICATION_SUMMARY_{timestamp}.md"
        with open(md_path, 'w') as f:
            self._write_markdown_report(f, summary)

        return json_path, md_path

    def _write_markdown_report(self, f, summary: Dict):
        """
        Write markdown formatted report.

        Args:
            f: File handle
            summary: Summary dictionary
        """
        f.write("# ETL Verification Summary Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Current Month:** {summary['current_month']}\n\n")
        f.write(f"**Backfill Month:** {summary['backfill_month']}\n\n")
        f.write(f"**Duration:** {summary['duration_seconds']:.1f} seconds\n\n")

        # Overall statistics
        f.write("## Overall Statistics\n\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Total Verifications | {summary['total_verifications']} |\n")
        f.write(f"| Passed | {summary['passed']} |\n")
        f.write(f"| Failed | {summary['failed']} |\n")
        f.write(f"| Skipped | {summary['skipped']} |\n")
        f.write(f"| Errors | {summary['errors']} |\n")
        f.write(f"| Overall Pass Rate | {summary['overall_pass_rate']:.1f}% |\n\n")

        # Individual verifications
        f.write("## Individual Verifications\n\n")
        f.write("| Priority | Name | Status | Pass Rate | Issues | Report |\n")
        f.write("|----------|------|--------|-----------|--------|--------|\n")

        for result in summary['verifications']:
            name = result['name']
            priority = result['priority']
            status = result['status']
            pass_rate = result.get('pass_rate', 0.0)
            issue_count = len(result.get('issues', []))
            report_path = result.get('report_path', 'N/A')

            # Status emoji
            if status == "PASSED":
                status_display = "[OK] PASSED"
            elif status == "FAILED":
                status_display = "[FAIL] FAILED"
            elif status == "SKIPPED":
                status_display = "[SKIP] SKIPPED"
            else:
                status_display = "[ERROR] ERROR"

            f.write(f"| {priority} | {name} | {status_display} | {pass_rate:.1f}% | {issue_count} | ")
            if report_path and report_path != 'N/A':
                report_name = Path(report_path).name
                f.write(f"[{report_name}]({report_path})")
            else:
                f.write("N/A")
            f.write(" |\n")

        # Detailed issues
        f.write("\n## Detailed Issues\n\n")
        for result in summary['verifications']:
            if result.get('issues'):
                f.write(f"### {result['name']}\n\n")
                f.write(f"**Status:** {result['status']}\n\n")
                f.write("**Issues:**\n\n")
                for issue in result['issues']:
                    f.write(f"- {issue}\n")
                f.write("\n")

        # Recommendations
        f.write("## Recommendations\n\n")
        if summary['failed'] > 0:
            f.write("### Failed Verifications\n\n")
            f.write("Review the detailed reports for failed verifications and investigate discrepancies.\n\n")

        if summary['skipped'] > 0:
            f.write("### Skipped Verifications\n\n")
            f.write("The following verifications were skipped due to missing export files:\n\n")
            for result in summary['verifications']:
                if result['status'] == 'SKIPPED':
                    f.write(f"- **{result['name']}**: {', '.join(result['issues'])}\n")
            f.write("\n")
            f.write("To complete these verifications:\n")
            f.write("1. Export the required CSV files from Power BI visuals\n")
            f.write("2. Place them in the appropriate outputs directory\n")
            f.write("3. Re-run the verification\n\n")

        if summary['errors'] > 0:
            f.write("### Errors\n\n")
            f.write("The following verifications encountered errors:\n\n")
            for result in summary['verifications']:
                if result['status'] == 'ERROR':
                    f.write(f"- **{result['name']}**: {', '.join(result['issues'])}\n")
            f.write("\n")


def main():
    """Run all verifications."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Run all ETL verifications")
    parser.add_argument(
        "--current-month",
        default="2025_12",
        help="Current month to verify (default: 2025_12)"
    )
    parser.add_argument(
        "--backfill-month",
        default="2025_11",
        help="Backfill month for comparison (default: 2025_11)"
    )
    args = parser.parse_args()

    # Run verifications
    runner = VerificationRunner(
        current_month=args.current_month,
        backfill_month=args.backfill_month
    )

    summary = runner.run_all_verifications()

    # Write summary report
    json_path, md_path = runner.write_summary_report(summary)

    # Print final summary
    print()
    print("=" * 80)
    print("VERIFICATION SUITE COMPLETE")
    print("=" * 80)
    print(f"Total Verifications: {summary['total_verifications']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Errors: {summary['errors']}")
    print(f"Overall Pass Rate: {summary['overall_pass_rate']:.1f}%")
    print()
    print("Reports generated:")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
