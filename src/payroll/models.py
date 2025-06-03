"""
Models module for defining data structures used in the payroll system.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Employee:
    """
    Employee data structure.
    
    Attributes:
        id: Employee ID
        name: Employee name
        email: Employee email
        department: Employee department
        hours_worked: Hours worked by the employee
        hourly_rate: Hourly rate of the employee
    """
    id: int
    name: str
    email: str
    department: str
    hours_worked: float
    hourly_rate: float
    
    def calculate_payout(self) -> float:
        """
        Calculate the payout for the employee.
        
        Returns:
            Payout amount
        """
        return self.hours_worked * self.hourly_rate