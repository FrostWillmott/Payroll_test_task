"""
Tests for the main script.
"""

import os
import sys
import pytest
from unittest.mock import patch
import json

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import parse_arguments, main


def test_parse_arguments():
    """Test parsing command line arguments."""
    # Test with required arguments
    with patch('sys.argv', ['main.py', 'data1.csv', '--report', 'payout']):
        args = parse_arguments()
        assert args.files == ['data1.csv']
        assert args.report == 'payout'

    # Test with multiple files
    with patch('sys.argv', ['main.py', 'data1.csv', 'data2.csv', '--report', 'payout']):
        args = parse_arguments()
        assert args.files == ['data1.csv', 'data2.csv']
        assert args.report == 'payout'


def test_main_success():
    """Test the main function with valid arguments."""
    # Create a temporary CSV file
    file_path = "test_main.csv"
    with open(file_path, "w") as f:
        f.write("id,email,name,department,hours_worked,hourly_rate\n")
        f.write("1,alice@example.com,Alice Johnson,Marketing,160,50\n")

    try:
        # Test with valid arguments
        with patch('sys.argv', ['main.py', file_path, '--report', 'payout']):
            with patch('builtins.print') as mock_print:
                exit_code = main()

                # Check that the function returned success
                assert exit_code == 0

                # Check that something was printed
                mock_print.assert_called_once()

                # Get the printed report
                report_str = mock_print.call_args[0][0]

                # Parse the JSON report
                report = json.loads(report_str)

                # Check the structure
                assert "departments" in report
                assert "total_payout" in report

                # Check the departments
                departments = report["departments"]
                assert len(departments) == 1  # Only Marketing

                # Check the department
                department = departments[0]
                assert department["name"] == "Marketing"
                assert len(department["employees"]) == 1
                assert department["employees"][0]["name"] == "Alice Johnson"
                assert department["employees"][0]["payout"] == 8000.0
                assert department["department_total"] == 8000.0

                # Check the total payout
                assert report["total_payout"] == 8000.0
    finally:
        # Clean up
        os.remove(file_path)


def test_main_file_not_found():
    """Test the main function with a non-existent file."""
    with patch('sys.argv', ['main.py', 'nonexistent.csv', '--report', 'payout']):
        with patch('sys.stderr') as mock_stderr:
            exit_code = main()

            # Check that the function returned an error
            assert exit_code == 1


def test_main_unsupported_report_type():
    """Test the main function with an unsupported report type."""
    # Create a temporary CSV file
    file_path = "test_main.csv"
    with open(file_path, "w") as f:
        f.write("id,email,name,department,hours_worked,hourly_rate\n")
        f.write("1,alice@example.com,Alice Johnson,Marketing,160,50\n")

    try:
        # Test with an unsupported report type
        with patch('sys.argv', ['main.py', file_path, '--report', 'unsupported']):
            with patch('sys.stderr') as mock_stderr:
                exit_code = main()

                # Check that the function returned an error
                assert exit_code == 1
    finally:
        # Clean up
        os.remove(file_path)


def test_main_with_real_data():
    """Test the main function with real data files."""
    file_paths = ["data/data1.csv", "data/data2.csv", "data/data3.csv"]

    # Check if the files exist
    for file_path in file_paths:
        assert os.path.exists(file_path), f"Test data file {file_path} not found"

    # Test with real data files
    with patch('sys.argv', ['main.py'] + file_paths + ['--report', 'payout']):
        with patch('builtins.print') as mock_print:
            exit_code = main()

            # Check that the function returned success
            assert exit_code == 0

            # Check that something was printed
            mock_print.assert_called_once()

            # Get the printed report
            report_str = mock_print.call_args[0][0]

            # Parse the JSON report
            report = json.loads(report_str)

            # Check the structure
            assert "departments" in report
            assert "total_payout" in report

            # Check that we have the expected number of departments
            departments = report["departments"]
            assert len(departments) == 5  # Marketing, Design, Engineering, Finance, HR
