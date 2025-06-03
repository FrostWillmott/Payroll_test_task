"""
CSV Parser module for reading and parsing employee data from CSV files.
"""

from typing import Dict, List, Any, Optional, Union
import os
from .models import Employee


def parse_csv_files(file_paths: List[str], as_dataclass: bool = False) -> Union[List[Dict[str, Any]], List[Employee]]:
    """
    Parse multiple CSV files containing employee data.

    Args:
        file_paths: List of paths to CSV files
        as_dataclass: If True, returns Employee objects instead of dictionaries

    Returns:
        List of dictionaries or Employee objects containing employee data

    Raises:
        FileNotFoundError: If any of the files doesn't exist
        ValueError: If there's an issue parsing the CSV data
    """
    all_employees = []

    for file_path in file_paths:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        employees = parse_csv_file(file_path, as_dataclass)
        all_employees.extend(employees)

    return all_employees


def parse_csv_file(file_path: str, as_dataclass: bool = False) -> Union[List[Dict[str, Any]], List[Employee]]:
    """
    Parse a single CSV file containing employee data.

    Args:
        file_path: Path to the CSV file
        as_dataclass: If True, returns Employee objects instead of dictionaries

    Returns:
        List of dictionaries or Employee objects containing employee data

    Raises:
        ValueError: If there's an issue parsing the CSV data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        if not lines:
            return []

        # Parse header
        header = parse_csv_line(lines[0])

        # Find the index of the hourly rate column (could be named differently)
        rate_column_index = find_rate_column_index(header)
        if rate_column_index is None:
            raise ValueError(f"Could not find hourly rate column in {file_path}")

        # Parse employee data
        employees = []
        for line in lines[1:]:
            if line.strip():  # Skip empty lines
                employee = parse_employee_line(line, header, rate_column_index)
                employees.append(employee)

        # Convert to Employee objects if requested
        if as_dataclass:
            return [
                Employee(
                    id=employee["id"],
                    name=employee["name"],
                    email=employee["email"],
                    department=employee["department"],
                    hours_worked=employee["hours_worked"],
                    hourly_rate=employee["hourly_rate"]
                )
                for employee in employees
            ]

        return employees
    except Exception as e:
        raise ValueError(f"Error parsing CSV file {file_path}: {str(e)}")


def parse_csv_line(line: str) -> List[str]:
    """
    Parse a CSV line into a list of values.

    Args:
        line: CSV line

    Returns:
        List of values
    """
    return [value.strip() for value in line.strip().split(',')]


def find_rate_column_index(header: List[str]) -> Optional[int]:
    """
    Find the index of the hourly rate column in the header.
    It could be named 'hourly_rate', 'rate', or 'salary'.

    Args:
        header: List of column names

    Returns:
        Index of the hourly rate column or None if not found
    """
    rate_column_names = ['hourly_rate', 'rate', 'salary']
    for name in rate_column_names:
        if name in header:
            return header.index(name)
    return None


def parse_employee_line(line: str, header: List[str], rate_column_index: int) -> Dict[str, Any]:
    """
    Parse a CSV line containing employee data.

    Args:
        line: CSV line
        header: List of column names
        rate_column_index: Index of the hourly rate column

    Returns:
        Dictionary containing employee data

    Raises:
        ValueError: If there's an issue parsing the employee data
    """
    values = parse_csv_line(line)

    if len(values) != len(header):
        raise ValueError(f"Number of values ({len(values)}) doesn't match header length ({len(header)})")

    employee = {}
    for i, column_name in enumerate(header):
        # Convert numeric values
        if column_name == 'id':
            employee[column_name] = int(values[i])
        elif column_name == 'hours_worked' or i == rate_column_index:
            employee[column_name] = float(values[i])
        else:
            employee[column_name] = values[i]

    # Standardize the hourly rate column name to 'hourly_rate'
    if header[rate_column_index] != 'hourly_rate':
        employee['hourly_rate'] = employee.pop(header[rate_column_index])

    return employee
