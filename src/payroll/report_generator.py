"""
Report Generator module for generating different types of reports from employee data.
"""

from typing import Dict, List, Any, Callable, Optional
import json


# Type for report generator functions
ReportGeneratorFunc = Callable[[List[Dict[str, Any]]], str]


# Registry of report generators
_report_generators: Dict[str, ReportGeneratorFunc] = {}


def register_report_generator(report_type: str) -> Callable[[ReportGeneratorFunc], ReportGeneratorFunc]:
    """
    Decorator to register a report generator function.

    Args:
        report_type: Type of report (e.g., 'payout')

    Returns:
        Decorator function
    """
    def decorator(func: ReportGeneratorFunc) -> ReportGeneratorFunc:
        _report_generators[report_type] = func
        return func
    return decorator


def generate_report(employees: List[Dict[str, Any]], report_type: str) -> str:
    """
    Generate a report of the specified type.

    Args:
        employees: List of dictionaries containing employee data
        report_type: Type of report to generate

    Returns:
        Generated report as a string

    Raises:
        ValueError: If the report type is not supported
    """
    generator = _report_generators.get(report_type)
    if not generator:
        supported_reports = ", ".join(_report_generators.keys())
        raise ValueError(
            f"Unsupported report type: {report_type}. "
            f"Supported types: {supported_reports or 'none'}"
        )
    
    return generator(employees)


@register_report_generator("payout")
def generate_payout_report(employees: List[Dict[str, Any]]) -> str:
    """
    Generate a payout report.

    Args:
        employees: List of dictionaries containing employee data

    Returns:
        Payout report as a JSON string
    """
    # Calculate payout for each employee
    payouts = []
    for employee in employees:
        payout = calculate_payout(employee)
        payouts.append({
            "id": employee["id"],
            "name": employee["name"],
            "email": employee["email"],
            "department": employee["department"],
            "hours_worked": employee["hours_worked"],
            "hourly_rate": employee["hourly_rate"],
            "payout": payout
        })
    
    # Sort by department and then by name
    payouts.sort(key=lambda x: (x["department"], x["name"]))
    
    # Group by department
    departments = {}
    for payout in payouts:
        department = payout["department"]
        if department not in departments:
            departments[department] = []
        departments[department].append(payout)
    
    # Calculate department totals
    report = {
        "departments": [],
        "total_payout": 0
    }
    
    for department, employees in departments.items():
        department_total = sum(employee["payout"] for employee in employees)
        report["departments"].append({
            "name": department,
            "employees": employees,
            "department_total": department_total
        })
        report["total_payout"] += department_total
    
    return json.dumps(report, indent=2)


def calculate_payout(employee: Dict[str, Any]) -> float:
    """
    Calculate the payout for an employee.

    Args:
        employee: Dictionary containing employee data

    Returns:
        Payout amount
    """
    return employee["hours_worked"] * employee["hourly_rate"]