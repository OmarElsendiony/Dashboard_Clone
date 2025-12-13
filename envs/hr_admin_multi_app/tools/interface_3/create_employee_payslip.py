import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict

from tau_bench.envs.tool import Tool


class CreateEmployeePayslip(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        cycle_id: str,
    ) -> str:
        """
        Create a payslip for an employee in a payroll cycle.
        Net pay is automatically calculated as gross_pay minus total deductions.
        
        Args:
            data: The database dictionary containing all tables.
            employee_id: The ID of the employee (required).
            cycle_id: The ID of the payroll cycle (required).
        
        Returns:
            JSON string with the created payslip record including gross_pay, 
            net_pay_value, and payroll_variance_percent.
        """
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            max_id = 0
            for k in table.keys():
                try:
                    max_id = max(max_id, int(k))
                except ValueError:
                    continue
            return str(max_id + 1)

        def calculate_gross_pay(hours: float, overtime: float, hourly_rate: Decimal) -> Decimal:
            """
            Calculate gross pay using formula:
            gross_pay = (hours_worked × hourly_rate) + (overtime_hours × hourly_rate × 1.5)
            """
            regular_pay = Decimal(str(hours)) * hourly_rate
            overtime_pay = Decimal(str(overtime)) * hourly_rate * Decimal("1.5")
            return (regular_pay + overtime_pay).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        def calculate_variance_percent(previous_gross: Decimal, current_gross: Decimal) -> Decimal:
            """
            Calculate payroll variance percent using formula:
            payroll_variance_percent = ((previous_gross_pay - current_gross_pay) / previous_gross_pay) × 100
            """
            if previous_gross <= 0:
                return Decimal("0.00")
            variance = ((previous_gross - current_gross) / previous_gross) * Decimal("100")
            return variance.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        def calculate_total_deductions(
            data: Dict[str, Any], 
            employee_id: str, 
            cycle_id: str,
            gross_pay: Decimal
        ) -> Decimal:
            """
            Calculate total deductions for the employee in the given cycle.
            Includes payroll deductions (taxes, benefits, garnishments, voluntary deductions).
            """
            total_deductions = Decimal("0.00")
            payroll_deductions = data.get("payroll_deductions", {})
            
            for deduction in payroll_deductions.values():
                if deduction.get("employee_id") == employee_id:
                    # Check if deduction is active
                    if deduction.get("status") == "inactive":
                        continue
                    
                    deduction_amount = Decimal(str(deduction.get("amount", 0) or 0))
                    total_deductions += deduction_amount
            
            return total_deductions.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        if not employee_id:
            return json.dumps({"error": "Missing required parameter: employee_id is required"})
        if not cycle_id:
            return json.dumps({"error": "Missing required parameter: cycle_id is required"})

        employee_id = str(employee_id)
        cycle_id = str(cycle_id)

        employees = data.get("employees", {})
        payroll_cycles = data.get("payroll_cycles", {})
        payslips = data.get("payslips", {})
        payroll_inputs = data.get("payroll_inputs", {})

        if employee_id not in employees:
            return json.dumps({"error": f"Employee with ID '{employee_id}' not found"})

        employee = employees[employee_id]

        if cycle_id not in payroll_cycles:
            return json.dumps({"error": f"Payroll cycle with ID '{cycle_id}' not found"})

        cycle = payroll_cycles[cycle_id]

        # Check for existing payslip for this employee/cycle combination
        for payslip_id, payslip in payslips.items():
            if payslip.get("employee_id") == employee_id and payslip.get("cycle_id") == cycle_id:
                return json.dumps({
                    "error": f"Payslip for employee '{employee_id}' in cycle '{cycle_id}' already exists"
                })

        # Calculate hourly rate from base_salary (annual salary / 2080 standard work hours)
        base_salary = Decimal(str(employee.get("base_salary", 0) or 0))
        hourly_rate = (base_salary / Decimal("2080")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Find payroll input for this employee/cycle to get hours
        current_hours = 0.0
        current_overtime = 0.0
        for pinput in payroll_inputs.values():
            if pinput.get("employee_id") == employee_id and pinput.get("cycle_id") == cycle_id:
                current_hours = float(pinput.get("hours_worked", 0) or 0)
                current_overtime = float(pinput.get("overtime_hours", 0) or 0)
                break

        # Calculate current gross pay
        current_gross_pay = calculate_gross_pay(current_hours, current_overtime, hourly_rate)

        # Calculate total deductions
        total_deductions = calculate_total_deductions(data, employee_id, cycle_id, current_gross_pay)

        # Calculate net pay value: gross_pay - total_deductions
        net_pay_value = (current_gross_pay - total_deductions).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        # Ensure net pay is not negative
        if net_pay_value < 0:
            net_pay_value = Decimal("0.00")

        # Find previous payroll input for this employee to calculate variance
        previous_gross_pay = None
        current_cycle_start = cycle.get("start_date", "")

        for pinput in payroll_inputs.values():
            if pinput.get("employee_id") == employee_id and pinput.get("cycle_id") != cycle_id:
                prev_cycle_id = pinput.get("cycle_id")
                prev_cycle = payroll_cycles.get(prev_cycle_id, {})
                prev_cycle_start = prev_cycle.get("start_date", "")

                # Find the most recent previous cycle
                if prev_cycle_start < current_cycle_start:
                    prev_hours = float(pinput.get("hours_worked", 0) or 0)
                    prev_overtime = float(pinput.get("overtime_hours", 0) or 0)
                    prev_gross = calculate_gross_pay(prev_hours, prev_overtime, hourly_rate)

                    if previous_gross_pay is None or prev_cycle_start > previous_gross_pay[1]:
                        previous_gross_pay = (prev_gross, prev_cycle_start)

        # Calculate variance if previous input exists
        payroll_variance_percent = None
        if previous_gross_pay is not None:
            payroll_variance_percent = float(calculate_variance_percent(previous_gross_pay[0], current_gross_pay))

        # Generate new payslip ID
        payslip_id = generate_id(payslips)

        # Create payslip record
        timestamp = "2025-11-16T23:59:00"
        new_payslip = {
            "payslip_id": payslip_id,
            "employee_id": employee_id,
            "cycle_id": cycle_id,
            "hours_worked": current_hours,
            "overtime_hours": current_overtime,
            "hourly_rate": float(hourly_rate),
            "gross_pay": float(current_gross_pay),
            "total_deductions": float(total_deductions),
            "payroll_variance_percent": payroll_variance_percent,
            "net_pay_value": float(net_pay_value),
            "status": "draft",
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        payslips[payslip_id] = new_payslip
        data["payslips"] = payslips

        return json.dumps(new_payslip)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_employee_payslip",
                "description": (
                    "Creates a payslip for an employee in a specific payroll cycle. "
                    "Each employee can only have one payslip per cycle. "
                    "Payslip is created with 'draft' status. "
                    "Automatically calculates gross_pay using formula: (hours_worked × hourly_rate) + (overtime_hours × hourly_rate × 1.5). "
                    "Automatically calculates net_pay_value as: gross_pay - total_deductions. "
                    "Calculates payroll_variance_percent if previous cycle exists using formula: "
                    "((previous_gross_pay - current_gross_pay) / previous_gross_pay) × 100."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The ID of the employee (required).",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "The ID of the payroll cycle (required).",
                        },
                    },
                    "required": ["employee_id", "cycle_id"],
                },
            },
        }
