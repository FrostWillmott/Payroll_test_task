"""
Report Protocols module for defining interfaces for report generation.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .models import Employee


class ReportGenerator(ABC):
    """
    Abstract base class for report generators.
    """
    
    @abstractmethod
    def generate(self, employees: List[Employee]) -> str:
        """
        Generate a report.
        
        Args:
            employees: List of Employee objects
            
        Returns:
            Generated report as a string
        """
        pass


class PayoutReportGenerator(ReportGenerator):
    """
    Payout report generator.
    """
    
    def generate(self, employees: List[Employee]) -> str:
        """
        Generate a payout report.
        
        Args:
            employees: List of Employee objects
            
        Returns:
            Payout report as a JSON string
        """
        import json
        
        # Calculate payout for each employee
        payouts = []
        for employee in employees:
            payout = employee.calculate_payout()
            payouts.append({
                "id": employee.id,
                "name": employee.name,
                "email": employee.email,
                "department": employee.department,
                "hours_worked": employee.hours_worked,
                "hourly_rate": employee.hourly_rate,
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
        
        for department, dept_employees in departments.items():
            department_total = sum(employee["payout"] for employee in dept_employees)
            report["departments"].append({
                "name": department,
                "employees": dept_employees,
                "department_total": department_total
            })
            report["total_payout"] += department_total
        
        return json.dumps(report, indent=2)