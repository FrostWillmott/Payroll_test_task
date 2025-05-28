"""
Tests for the report generator module.
"""

import json
import pytest
from src.payroll.report_generator import (
    generate_report,
    register_report_generator,
    calculate_payout,
    _report_generators
)


def test_calculate_payout():
    """Test calculating the payout for an employee."""
    employee = {
        "hours_worked": 160.0,
        "hourly_rate": 50.0
    }
    assert calculate_payout(employee) == 8000.0


def test_register_report_generator():
    """Test registering a report generator."""
    # Save the original report generators
    original_generators = _report_generators.copy()

    try:
        # Register a test report generator
        @register_report_generator("test")
        def test_generator(employees):
            return "Test report"

        # Check that it was registered
        assert "test" in _report_generators
        assert _report_generators["test"] == test_generator

        # Check that it works
        assert test_generator([]) == "Test report"
    finally:
        # Restore the original report generators
        _report_generators.clear()
        _report_generators.update(original_generators)


def test_generate_report_unsupported_type():
    """Test that generate_report raises ValueError for unsupported report types."""
    with pytest.raises(ValueError):
        generate_report([], "unsupported")


def test_generate_payout_report():
    """Test generating a payout report."""
    employees = [
        {
            "id": 1,
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "department": "Marketing",
            "hours_worked": 160.0,
            "hourly_rate": 50.0
        },
        {
            "id": 2,
            "name": "Bob Smith",
            "email": "bob@example.com",
            "department": "Design",
            "hours_worked": 150.0,
            "hourly_rate": 40.0
        },
        {
            "id": 3,
            "name": "Carol Williams",
            "email": "carol@example.com",
            "department": "Design",
            "hours_worked": 170.0,
            "hourly_rate": 60.0
        }
    ]

    report = generate_report(employees, "payout")

    # Parse the JSON report
    report_data = json.loads(report)

    # Check the structure
    assert "departments" in report_data
    assert "total_payout" in report_data

    # Check the departments
    departments = report_data["departments"]
    assert len(departments) == 2  # Marketing and Design

    # Check the department names
    department_names = [dept["name"] for dept in departments]
    assert "Marketing" in department_names
    assert "Design" in department_names

    # Check the employees in each department
    for dept in departments:
        if dept["name"] == "Marketing":
            assert len(dept["employees"]) == 1
            assert dept["employees"][0]["name"] == "Alice Johnson"
            assert dept["employees"][0]["payout"] == 8000.0
            assert dept["department_total"] == 8000.0
        elif dept["name"] == "Design":
            assert len(dept["employees"]) == 2
            # Employees should be sorted by name
            assert dept["employees"][0]["name"] == "Bob Smith"
            assert dept["employees"][0]["payout"] == 6000.0
            assert dept["employees"][1]["name"] == "Carol Williams"
            assert dept["employees"][1]["payout"] == 10200.0
            assert dept["department_total"] == 16200.0

    # Check the total payout
    assert report_data["total_payout"] == 24200.0


def test_generate_report_with_real_data():
    """Test generating a report with real data."""
    from src.payroll.csv_parser import parse_csv_files

    # Parse the real data files
    file_paths = ["data/data1.csv", "data/data2.csv", "data/data3.csv"]
    employees = parse_csv_files(file_paths)

    # Generate a payout report
    report = generate_report(employees, "payout")

    # Parse the JSON report
    report_data = json.loads(report)

    # Check the structure
    assert "departments" in report_data
    assert "total_payout" in report_data

    # Check that we have the expected number of departments
    departments = report_data["departments"]
    assert len(departments) == 5  # Marketing, Design, Engineering, Finance, HR

    # Check that the total payout is correct
    total_payout = sum(dept["department_total"] for dept in departments)
    assert report_data["total_payout"] == total_payout
