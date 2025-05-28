# Payroll Report Generator

A command-line tool for generating payroll reports from CSV files containing employee data.

## Features

- Read employee data from multiple CSV files
- Generate payout reports
- Support for different CSV formats (different column names for hourly rate)
- Extensible architecture for adding new report types

## Installation

Clone the repository:

```bash
git clone https://github.com/frostwillmott/payroll-test-task.git
cd payroll-test-task
```

## Usage

Run the script with one or more CSV files and specify the report type:

```bash
python main.py data1.csv data2.csv data3.csv --report payout
```

### Arguments

- `files`: One or more CSV files containing employee data
- `--report`: Type of report to generate (e.g., payout)

### CSV File Format

The CSV files should contain the following columns:
- `id`: Employee ID
- `name`: Employee name
- `email`: Employee email
- `department`: Employee department
- `hours_worked`: Hours worked by the employee
- `hourly_rate` (or `rate` or `salary`): Hourly rate of the employee

Example:
```
id,email,name,department,hours_worked,hourly_rate
1,alice@example.com,Alice Johnson,Marketing,160,50
2,bob@example.com,Bob Smith,Design,150,40
3,carol@example.com,Carol Williams,Design,170,60
```

## Adding New Report Types

The project is designed to be easily extensible with new report types. Here's how to add a new report type:

1. Open `src/payroll/report_generator.py`
2. Create a new function that takes a list of employee dictionaries and returns a string
3. Decorate the function with `@register_report_generator("your_report_type")`

Example:

```python
@register_report_generator("average_rate")
def generate_average_rate_report(employees: List[Dict[str, Any]]) -> str:
    """
    Generate a report showing the average hourly rate by department.
    
    Args:
        employees: List of dictionaries containing employee data
        
    Returns:
        Report as a JSON string
    """
    # Group employees by department
    departments = {}
    for employee in employees:
        department = employee["department"]
        if department not in departments:
            departments[department] = []
        departments[department].append(employee)
    
    # Calculate average hourly rate for each department
    report = {
        "departments": [],
        "overall_average": 0
    }
    
    total_rate_sum = 0
    total_employees = 0
    
    for department, dept_employees in departments.items():
        rate_sum = sum(employee["hourly_rate"] for employee in dept_employees)
        avg_rate = rate_sum / len(dept_employees)
        
        report["departments"].append({
            "name": department,
            "average_rate": avg_rate,
            "employee_count": len(dept_employees)
        })
        
        total_rate_sum += rate_sum
        total_employees += len(dept_employees)
    
    # Sort departments by name
    report["departments"].sort(key=lambda x: x["name"])
    
    # Calculate overall average
    report["overall_average"] = total_rate_sum / total_employees
    
    return json.dumps(report, indent=2)
```

After adding the new report type, you can use it with:

```bash
python main.py data1.csv data2.csv data3.csv --report average_rate
```

## Testing

Run the tests with pytest:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.