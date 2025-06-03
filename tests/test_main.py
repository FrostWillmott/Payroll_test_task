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


@pytest.fixture
def temp_csv_file():
    """Fixture for a temporary CSV file."""
    file_path = "test_main.csv"
    with open(file_path, "w") as f:
        f.write("id,email,name,department,hours_worked,hourly_rate\n")
        f.write("1,alice@example.com,Alice Johnson,Marketing,160,50\n")

    yield file_path

    # Clean up
    if os.path.exists(file_path):
        os.remove(file_path)


@pytest.fixture
def real_data_file_paths():
    """Fixture for real data file paths."""
    file_paths = ["data/data1.csv", "data/data2.csv", "data/data3.csv"]

    # Check if the files exist
    for file_path in file_paths:
        assert os.path.exists(file_path), f"Test data file {file_path} not found"

    return file_paths


@pytest.mark.parametrize("files,report_type", [
    (['data1.csv'], 'payout'),
    (['data1.csv', 'data2.csv'], 'payout')
])
def test_parse_arguments(files, report_type):
    """Test parsing command line arguments."""
    with patch('sys.argv', ['main.py'] + files + ['--report', report_type]):
        args = parse_arguments()
        assert args.files == files
        assert args.report == report_type


def test_main_success(temp_csv_file):
    """Test the main function with valid arguments."""
    with patch('sys.argv', ['main.py', temp_csv_file, '--report', 'payout']):
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


def test_main_file_not_found():
    """Test the main function with a non-existent file."""
    with patch('sys.argv', ['main.py', 'nonexistent.csv', '--report', 'payout']):
        with patch('sys.stderr') as mock_stderr:
            exit_code = main()

            # Check that the function returned an error
            assert exit_code == 1


@pytest.mark.parametrize("report_type,expected_exit_code", [
    ('payout', 0),
    ('unsupported', 1)
])
def test_main_report_type(temp_csv_file, report_type, expected_exit_code):
    """Test the main function with different report types."""
    with patch('sys.argv', ['main.py', temp_csv_file, '--report', report_type]):
        if expected_exit_code == 0:
            with patch('builtins.print') as mock_print:
                exit_code = main()
                assert exit_code == expected_exit_code
                mock_print.assert_called_once()
        else:
            with patch('sys.stderr') as mock_stderr:
                exit_code = main()
                assert exit_code == expected_exit_code


def test_main_with_real_data(real_data_file_paths):
    """Test the main function with real data files."""
    with patch('sys.argv', ['main.py'] + real_data_file_paths + ['--report', 'payout']):
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
