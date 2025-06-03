"""
Report Generator module for generating different types of reports from employee data.
"""

from typing import Dict, Type, List, Any, Optional, Union
from .models import Employee
from .report_protocols import ReportGenerator, PayoutReportGenerator


class ReportGeneratorFactory:
    """
    Factory class for creating report generators.
    """

    _generators: Dict[str, Type[ReportGenerator]] = {}

    @classmethod
    def register(cls, report_type: str, generator_class: Type[ReportGenerator]) -> None:
        """
        Register a report generator class.

        Args:
            report_type: Type of report (e.g., 'payout')
            generator_class: Report generator class
        """
        cls._generators[report_type] = generator_class

    @classmethod
    def create(cls, report_type: str) -> ReportGenerator:
        """
        Create a report generator of the specified type.

        Args:
            report_type: Type of report to generate

        Returns:
            Report generator instance

        Raises:
            ValueError: If the report type is not supported
        """
        generator_class = cls._generators.get(report_type)
        if not generator_class:
            supported_reports = ", ".join(cls._generators.keys())
            raise ValueError(
                f"Unsupported report type: {report_type}. "
                f"Supported types: {supported_reports or 'none'}"
            )

        return generator_class()


# Register report generators
ReportGeneratorFactory.register("payout", PayoutReportGenerator)

# For backward compatibility
_report_generators = ReportGeneratorFactory._generators


def generate_report(employees: Union[List[Dict[str, Any]], List[Employee]], report_type: str) -> str:
    """
    Generate a report of the specified type.

    Args:
        employees: List of dictionaries or Employee objects containing employee data
        report_type: Type of report to generate

    Returns:
        Generated report as a string

    Raises:
        ValueError: If the report type is not supported
    """
    # Convert dictionaries to Employee objects if needed
    if employees and not isinstance(employees[0], Employee):
        employee_objects = [
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
    else:
        employee_objects = employees

    # Create a report generator and generate the report
    generator = ReportGeneratorFactory.create(report_type)
    return generator.generate(employee_objects)
