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


def test_parse_csv_line():
    """Test parsing a CSV line."""
    line = "1,alice@example.com,Alice Johnson,Marketing,160,50"
    expected = ["1", "alice@example.com", "Alice Johnson", "Marketing", "160", "50"]
    assert parse_csv_line(line) == expected


def test_find_rate_column_index():
    """Test finding the hourly rate column index."""
    # Test with 'hourly_rate'
    header = ["id", "email", "name", "department", "hours_worked", "hourly_rate"]
    assert find_rate_column_index(header) == 5
    
    # Test with 'rate'
    header = ["id", "name", "email", "department", "hours_worked", "rate"]
    assert find_rate_column_index(header) == 5
    
    # Test with 'salary'
    header = ["department", "id", "name", "email", "hours_worked", "salary"]
    assert find_rate_column_index(header) == 5
    
    # Test with no rate column
    header = ["id", "name", "email", "department", "hours_worked"]
    assert find_rate_column_index(header) is None


def test_parse_employee_line():
    """Test parsing an employee line."""
    line = "1,alice@example.com,Alice Johnson,Marketing,160,50"
    header = ["id", "email", "name", "department", "hours_worked", "hourly_rate"]
    rate_column_index = 5
    
    expected = {
        "id": 1,
        "email": "alice@example.com",
        "name": "Alice Johnson",
        "department": "Marketing",
        "hours_worked": 160.0,
        "hourly_rate": 50.0
    }
    
    assert parse_employee_line(line, header, rate_column_index) == expected


def test_parse_employee_line_with_different_rate_column():
    """Test parsing an employee line with a different rate column name."""
    line = "4,David Lee,david@example.com,Engineering,180,70"
    header = ["id", "name", "email", "department", "hours_worked", "rate"]
    rate_column_index = 5
    
    expected = {
        "id": 4,
        "name": "David Lee",
        "email": "david@example.com",
        "department": "Engineering",
        "hours_worked": 180.0,
        "hourly_rate": 70.0  # Note: standardized to 'hourly_rate'
    }
    
    assert parse_employee_line(line, header, rate_column_index) == expected


def test_parse_employee_line_value_error():
    """Test that parse_employee_line raises ValueError when values don't match header."""
    line = "1,alice@example.com,Alice Johnson,Marketing,160"
    header = ["id", "email", "name", "department", "hours_worked", "hourly_rate"]
    rate_column_index = 5
    
    with pytest.raises(ValueError):
        parse_employee_line(line, header, rate_column_index)


def test_parse_csv_file():
    """Test parsing a CSV file."""
    # Create a temporary CSV file
    file_path = "test_data.csv"
    with open(file_path, "w") as f:
        f.write("id,email,name,department,hours_worked,hourly_rate\n")
        f.write("1,alice@example.com,Alice Johnson,Marketing,160,50\n")
    
    try:
        result = parse_csv_file(file_path)
        expected = [{
            "id": 1,
            "email": "alice@example.com",
            "name": "Alice Johnson",
            "department": "Marketing",
            "hours_worked": 160.0,
            "hourly_rate": 50.0
        }]
        assert result == expected
    finally:
        # Clean up
        os.remove(file_path)


def test_parse_csv_file_empty():
    """Test parsing an empty CSV file."""
    # Create a temporary empty CSV file
    file_path = "empty.csv"
    with open(file_path, "w") as f:
        pass
    
    try:
        result = parse_csv_file(file_path)
        assert result == []
    finally:
        # Clean up
        os.remove(file_path)


def test_parse_csv_file_no_rate_column():
    """Test that parse_csv_file raises ValueError when no rate column is found."""
    # Create a temporary CSV file without a rate column
    file_path = "no_rate.csv"
    with open(file_path, "w") as f:
        f.write("id,email,name,department,hours_worked\n")
        f.write("1,alice@example.com,Alice Johnson,Marketing,160\n")
    
    try:
        with pytest.raises(ValueError):
            parse_csv_file(file_path)
    finally:
        # Clean up
        os.remove(file_path)


def test_parse_csv_files():
    """Test parsing multiple CSV files."""
    # Create temporary CSV files
    file_paths = ["test_data1.csv", "test_data2.csv"]
    
    with open(file_paths[0], "w") as f:
        f.write("id,email,name,department,hours_worked,hourly_rate\n")
        f.write("1,alice@example.com,Alice Johnson,Marketing,160,50\n")
    
    with open(file_paths[1], "w") as f:
        f.write("id,name,email,department,hours_worked,rate\n")
        f.write("2,Bob Smith,bob@example.com,Design,150,40\n")
    
    try:
        result = parse_csv_files(file_paths)
        expected = [
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
        assert result == expected
    finally:
        # Clean up
        for file_path in file_paths:
            os.remove(file_path)


def test_parse_csv_files_file_not_found():
    """Test that parse_csv_files raises FileNotFoundError when a file is not found."""
    with pytest.raises(FileNotFoundError):
        parse_csv_files(["nonexistent.csv"])


def test_parse_csv_files_with_real_data():
    """Test parsing the real data files."""
    file_paths = ["data/data1.csv", "data/data2.csv", "data/data3.csv"]
    
    # Check if the files exist
    for file_path in file_paths:
        assert os.path.exists(file_path), f"Test data file {file_path} not found"
    
    result = parse_csv_files(file_paths)
    
    # Check that we have the expected number of employees
    assert len(result) == 9
    
    # Check that all employees have the standardized 'hourly_rate' field
    for employee in result:
        assert "hourly_rate" in employee