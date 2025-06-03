"""
Tests for the CSV parser module.
"""

import os
import pytest
from src.payroll.csv_parser import (
    parse_csv_files,
    parse_csv_file,
    parse_csv_line,
    find_rate_column_index,
    parse_employee_line
)


@pytest.fixture
def csv_line():
    """Fixture for a CSV line."""
    return "1,alice@example.com,Alice Johnson,Marketing,160,50"


@pytest.fixture
def expected_csv_values():
    """Fixture for expected CSV values."""
    return ["1", "alice@example.com", "Alice Johnson", "Marketing", "160", "50"]


@pytest.fixture
def header_with_hourly_rate():
    """Fixture for a header with hourly_rate."""
    return ["id", "email", "name", "department", "hours_worked", "hourly_rate"]


@pytest.fixture
def header_with_rate():
    """Fixture for a header with rate."""
    return ["id", "name", "email", "department", "hours_worked", "rate"]


@pytest.fixture
def header_with_salary():
    """Fixture for a header with salary."""
    return ["department", "id", "name", "email", "hours_worked", "salary"]


@pytest.fixture
def header_without_rate():
    """Fixture for a header without rate."""
    return ["id", "name", "email", "department", "hours_worked"]


@pytest.fixture
def expected_employee():
    """Fixture for expected employee data."""
    return {
        "id": 1,
        "email": "alice@example.com",
        "name": "Alice Johnson",
        "department": "Marketing",
        "hours_worked": 160.0,
        "hourly_rate": 50.0
    }


@pytest.fixture
def expected_employee_with_rate():
    """Fixture for expected employee data with rate."""
    return {
        "id": 4,
        "name": "David Lee",
        "email": "david@example.com",
        "department": "Engineering",
        "hours_worked": 180.0,
        "hourly_rate": 70.0  # Note: standardized to 'hourly_rate'
    }


@pytest.fixture
def temp_csv_file():
    """Fixture for a temporary CSV file."""
    file_path = "test_data.csv"
    with open(file_path, "w") as f:
        f.write("id,email,name,department,hours_worked,hourly_rate\n")
        f.write("1,alice@example.com,Alice Johnson,Marketing,160,50\n")

    yield file_path

    # Clean up
    if os.path.exists(file_path):
        os.remove(file_path)


@pytest.fixture
def temp_empty_csv_file():
    """Fixture for a temporary empty CSV file."""
    file_path = "empty.csv"
    with open(file_path, "w") as f:
        pass

    yield file_path

    # Clean up
    if os.path.exists(file_path):
        os.remove(file_path)


@pytest.fixture
def temp_csv_file_no_rate():
    """Fixture for a temporary CSV file without a rate column."""
    file_path = "no_rate.csv"
    with open(file_path, "w") as f:
        f.write("id,email,name,department,hours_worked\n")
        f.write("1,alice@example.com,Alice Johnson,Marketing,160\n")

    yield file_path

    # Clean up
    if os.path.exists(file_path):
        os.remove(file_path)


@pytest.fixture
def temp_multiple_csv_files():
    """Fixture for temporary multiple CSV files."""
    file_paths = ["test_data1.csv", "test_data2.csv"]

    with open(file_paths[0], "w") as f:
        f.write("id,email,name,department,hours_worked,hourly_rate\n")
        f.write("1,alice@example.com,Alice Johnson,Marketing,160,50\n")

    with open(file_paths[1], "w") as f:
        f.write("id,name,email,department,hours_worked,rate\n")
        f.write("2,Bob Smith,bob@example.com,Design,150,40\n")

    yield file_paths

    # Clean up
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)


@pytest.fixture
def expected_multiple_employees():
    """Fixture for expected multiple employee data."""
    return [
        {
            "id": 1,
            "email": "alice@example.com",
            "name": "Alice Johnson",
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
        }
    ]


@pytest.fixture
def real_data_file_paths():
    """Fixture for real data file paths."""
    return ["data/data1.csv", "data/data2.csv", "data/data3.csv"]


def test_parse_csv_line(csv_line, expected_csv_values):
    """Test parsing a CSV line."""
    assert parse_csv_line(csv_line) == expected_csv_values


@pytest.mark.parametrize("header,expected_index", [
    ("header_with_hourly_rate", 5),
    ("header_with_rate", 5),
    ("header_with_salary", 5),
    ("header_without_rate", None)
])
def test_find_rate_column_index(header, expected_index, request):
    """Test finding the hourly rate column index."""
    header_fixture = request.getfixturevalue(header)
    assert find_rate_column_index(header_fixture) == expected_index


def test_parse_employee_line(csv_line, header_with_hourly_rate, expected_employee):
    """Test parsing an employee line."""
    rate_column_index = 5
    assert parse_employee_line(csv_line, header_with_hourly_rate, rate_column_index) == expected_employee


def test_parse_employee_line_with_different_rate_column(header_with_rate, expected_employee_with_rate):
    """Test parsing an employee line with a different rate column name."""
    line = "4,David Lee,david@example.com,Engineering,180,70"
    rate_column_index = 5
    assert parse_employee_line(line, header_with_rate, rate_column_index) == expected_employee_with_rate


def test_parse_employee_line_value_error(header_with_hourly_rate):
    """Test that parse_employee_line raises ValueError when values don't match header."""
    line = "1,alice@example.com,Alice Johnson,Marketing,160"
    rate_column_index = 5

    with pytest.raises(ValueError):
        parse_employee_line(line, header_with_hourly_rate, rate_column_index)


def test_parse_csv_file(temp_csv_file, expected_employee):
    """Test parsing a CSV file."""
    result = parse_csv_file(temp_csv_file)
    assert result == [expected_employee]


def test_parse_csv_file_empty(temp_empty_csv_file):
    """Test parsing an empty CSV file."""
    result = parse_csv_file(temp_empty_csv_file)
    assert result == []


def test_parse_csv_file_no_rate_column(temp_csv_file_no_rate):
    """Test that parse_csv_file raises ValueError when no rate column is found."""
    with pytest.raises(ValueError):
        parse_csv_file(temp_csv_file_no_rate)


def test_parse_csv_files(temp_multiple_csv_files, expected_multiple_employees):
    """Test parsing multiple CSV files."""
    result = parse_csv_files(temp_multiple_csv_files)
    assert result == expected_multiple_employees


def test_parse_csv_files_file_not_found():
    """Test that parse_csv_files raises FileNotFoundError when a file is not found."""
    with pytest.raises(FileNotFoundError):
        parse_csv_files(["nonexistent.csv"])


def test_parse_csv_files_with_real_data(real_data_file_paths):
    """Test parsing the real data files."""
    # Check if the files exist
    for file_path in real_data_file_paths:
        assert os.path.exists(file_path), f"Test data file {file_path} not found"

    result = parse_csv_files(real_data_file_paths)

    # Check that we have the expected number of employees
    assert len(result) == 9

    # Check that all employees have the standardized 'hourly_rate' field
    for employee in result:
        assert "hourly_rate" in employee
