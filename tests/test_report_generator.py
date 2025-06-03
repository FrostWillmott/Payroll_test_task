"""
Tests for the report generator module.
"""

import json
import pytest
from src.payroll.models import Employee
from src.payroll.report_generator import (
    generate_report,
    ReportGeneratorFactory,
    _report_generators
)
from src.payroll.report_protocols import ReportGenerator


@pytest.fixture
def employee_data():
    """Fixture for employee data."""
    return [
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


@pytest.fixture
def employee_objects():
    """Fixture for employee objects."""
    return [
        Employee(
            id=1,
            name="Alice Johnson",
            email="alice@example.com",
            department="Marketing",
            hours_worked=160.0,
            hourly_rate=50.0
        ),
        Employee(
            id=2,
            name="Bob Smith",
            email="bob@example.com",
            department="Design",
            hours_worked=150.0,
            hourly_rate=40.0
        ),
        Employee(
            id=3,
            name="Carol Williams",
            email="carol@example.com",
            department="Design",
            hours_worked=170.0,
            hourly_rate=60.0
        )
    ]


@pytest.fixture
def real_data_file_paths():
    """Fixture for real data file paths."""
    return ["data/data1.csv", "data/data2.csv", "data/data3.csv"]


class TestReportGenerator(ReportGenerator):
    """Test report generator for testing."""

    def generate(self, employees):
        """Generate a test report."""
        return "Test report"


def test_employee_calculate_payout(employee_objects):
    """Test calculating the payout for an employee."""
    assert employee_objects[0].calculate_payout() == 8000.0


def test_report_generator_factory_register():
    """Test registering a report generator."""
    # Save the original report generators
    original_generators = _report_generators.copy()

    try:
        # Register a test report generator
        ReportGeneratorFactory.register("test", TestReportGenerator)

        # Check that it was registered
        assert "test" in _report_generators
        assert _report_generators["test"] == TestReportGenerator

        # Check that it works
        generator = ReportGeneratorFactory.create("test")
        assert isinstance(generator, TestReportGenerator)
        assert generator.generate([]) == "Test report"
    finally:
        # Restore the original report generators
        _report_generators.clear()
        _report_generators.update(original_generators)


def test_generate_report_unsupported_type():
    """Test that generate_report raises ValueError for unsupported report types."""
    with pytest.raises(ValueError):
        generate_report([], "unsupported")


@pytest.mark.parametrize("department,expected_employees,expected_total", [
    ("Marketing", 1, 8000.0),
    ("Design", 2, 16200.0)
])
def test_generate_payout_report_departments(employee_data, department, expected_employees, expected_total):
    """Test generating a payout report for specific departments."""
    report = generate_report(employee_data, "payout")
    report_data = json.loads(report)

    # Find the department in the report
    dept = next((d for d in report_data["departments"] if d["name"] == department), None)
    assert dept is not None

    # Check the department data
    assert len(dept["employees"]) == expected_employees
    assert dept["department_total"] == expected_total


def test_generate_payout_report(employee_data):
    """Test generating a payout report."""
    report = generate_report(employee_data, "payout")

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

    # Check the total payout
    assert report_data["total_payout"] == 24200.0


def test_generate_report_with_real_data(real_data_file_paths):
    """Test generating a report with real data."""
    from src.payroll.csv_parser import parse_csv_files

    # Parse the real data files
    employees = parse_csv_files(real_data_file_paths)

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
