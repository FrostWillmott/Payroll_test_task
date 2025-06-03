#!/usr/bin/env python3
"""
Payroll Report Generator

This script reads employee data from CSV files and generates reports.
"""

import argparse
import sys
from src.payroll.csv_parser import parse_csv_files
from src.payroll.report_generator import generate_report, _report_generators


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate payroll reports from CSV files."
    )
    parser.add_argument(
        "files", nargs="+", help="CSV files containing employee data"
    )
    parser.add_argument(
        "--report", 
        required=True, 
        choices=list(_report_generators.keys()),
        help="Type of report to generate (e.g., payout)"
    )
    return parser.parse_args()


def main() -> int:
    """Main entry point for the script."""
    args = parse_arguments()

    try:
        # Parse CSV files and get Employee objects
        employees_data = parse_csv_files(args.files, as_dataclass=True)

        # Generate and print the report
        report = generate_report(employees_data, args.report)
        print(report)

        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
