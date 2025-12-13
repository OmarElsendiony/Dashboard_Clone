import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class GeneratePayrollReport(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: Optional[str] = None,
        cycle_id: Optional[str] = None,
        department_id: Optional[str] = None,
    ) -> str:
        """
        Generate a comprehensive payroll report using payroll_cycles, payroll_inputs, 
        payslips, earnings, and deductions data.
        
        Args:
            data: The database dictionary containing all tables.
            employee_id: Filter by specific employee ID (optional).
            cycle_id: Filter by specific payroll cycle ID (optional).
            department_id: Filter by specific department ID (optional).
        
        Returns:
            JSON string with the payroll report including cycle info, inputs, payslips, 
            detailed earnings, and detailed deductions.
        """
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        # Require at least one filter parameter
        if not employee_id and not cycle_id and not department_id:
            return json.dumps({
                "success": False,
                "error": "At least one of 'employee_id', 'cycle_id', or 'department_id' must be provided"
            })

        employees = data.get("employees", {})
        payroll_cycles = data.get("payroll_cycles", {})
        payroll_inputs = data.get("payroll_inputs", {})
        payslips = data.get("payslips", {})
        payroll_earnings = data.get("payroll_earnings", {})
        deductions = data.get("deductions", {})
        departments = data.get("departments", {})

        # Validate filters if provided
        if employee_id:
            employee_id = str(employee_id)
            if employee_id not in employees:
                return json.dumps({"error": f"Employee with ID '{employee_id}' not found"})

        if cycle_id:
            cycle_id = str(cycle_id)
            if cycle_id not in payroll_cycles:
                return json.dumps({"error": f"Payroll cycle with ID '{cycle_id}' not found"})

        if department_id:
            department_id = str(department_id)
            if department_id not in departments:
                return json.dumps({"error": f"Department with ID '{department_id}' not found"})

        # Get relevant employee IDs based on filters
        relevant_employee_ids = None
        
        if employee_id:
            # Single employee filter
            relevant_employee_ids = {employee_id}
        elif department_id:
            # Department filter
            relevant_employee_ids = set()
            for emp_id, emp in employees.items():
                if emp.get("department_id") == department_id:
                    relevant_employee_ids.add(emp_id)

        # Get cycle info if filtering by cycle
        cycle_info = None
        if cycle_id:
            cycle = payroll_cycles.get(cycle_id, {})
            cycle_info = {
                "cycle_id": cycle_id,
                "start_date": cycle.get("start_date"),
                "end_date": cycle.get("end_date"),
                "frequency": cycle.get("frequency"),
                "status": cycle.get("status"),
            }

        # Build report data
        total_hours_worked = 0.0
        total_overtime_hours = 0.0
        total_earnings = 0.0
        total_deductions = 0.0
        total_net_pay = 0.0
        employee_details = []
        
        # Track cycle IDs when filtering by employee_id or department_id
        collected_cycle_ids = set()

        # Create a map of employee payroll data
        employee_payroll_map = {}

        # Process payroll inputs
        for input_id, pinput in payroll_inputs.items():
            emp_id = pinput.get("employee_id")
            c_id = pinput.get("cycle_id")

            # Apply filters
            if cycle_id and c_id != cycle_id:
                continue
            if relevant_employee_ids is not None and emp_id not in relevant_employee_ids:
                continue

            hours = float(pinput.get("hours_worked", 0) or 0)
            overtime = float(pinput.get("overtime_hours", 0) or 0)

            total_hours_worked += hours
            total_overtime_hours += overtime
            
            # Collect cycle IDs for later use
            if c_id:
                collected_cycle_ids.add(c_id)

            if emp_id not in employee_payroll_map:
                employee = employees.get(emp_id, {})
                employee_payroll_map[emp_id] = {
                    "employee_id": emp_id,
                    "employee_name": employee.get("full_name"),
                    "department_id": employee.get("department_id"),
                    "base_salary": employee.get("base_salary"),
                    "cycle_id": c_id,
                    "hours_worked": 0,
                    "overtime_hours": 0,
                    "payroll_variance_percent": pinput.get("payroll_variance_percent"),
                    "payroll_input_status": pinput.get("status"),
                    "earnings": [],
                    "total_earnings_amount": 0,
                    "deductions": [],
                    "total_deductions_amount": 0,
                    "net_pay_value": None,
                    "payslip_status": None,
                    "payslip_id": None,
                }

            employee_payroll_map[emp_id]["hours_worked"] += hours
            employee_payroll_map[emp_id]["overtime_hours"] += overtime
            employee_payroll_map[emp_id]["payroll_variance_percent"] = pinput.get("payroll_variance_percent")
            employee_payroll_map[emp_id]["payroll_input_status"] = pinput.get("status")
            employee_payroll_map[emp_id]["payroll_input_id"] = input_id

        # Process payslips
        for payslip_id, payslip in payslips.items():
            emp_id = payslip.get("employee_id")
            c_id = payslip.get("cycle_id")

            # Apply filters
            if cycle_id and c_id != cycle_id:
                continue
            if relevant_employee_ids is not None and emp_id not in relevant_employee_ids:
                continue

            net_pay = float(payslip.get("net_pay_value", 0) or 0)
            total_net_pay += net_pay
            
            # Collect cycle IDs for later use
            if c_id:
                collected_cycle_ids.add(c_id)

            if emp_id not in employee_payroll_map:
                employee = employees.get(emp_id, {})
                employee_payroll_map[emp_id] = {
                    "employee_id": emp_id,
                    "employee_name": employee.get("full_name"),
                    "department_id": employee.get("department_id"),
                    "base_salary": employee.get("base_salary"),
                    "cycle_id": c_id,
                    "hours_worked": 0,
                    "overtime_hours": 0,
                    "payroll_variance_percent": None,
                    "payroll_input_status": None,
                    "earnings": [],
                    "total_earnings_amount": 0,
                    "deductions": [],
                    "total_deductions_amount": 0,
                    "net_pay_value": None,
                    "payslip_status": None,
                    "payslip_id": None,
                }

            employee_payroll_map[emp_id]["net_pay_value"] = net_pay
            employee_payroll_map[emp_id]["payslip_status"] = payslip.get("status")
            employee_payroll_map[emp_id]["payslip_id"] = payslip_id

        # Process earnings (bonuses, commissions, etc.) - with detailed records
        for earning_id, earning in payroll_earnings.items():
            emp_id = earning.get("employee_id")
            c_id = earning.get("cycle_id")

            # Apply filters
            if cycle_id and c_id != cycle_id:
                continue
            if relevant_employee_ids is not None and emp_id not in relevant_employee_ids:
                continue

            amount = float(earning.get("amount", 0) or 0)
            total_earnings += amount
            
            # Collect cycle IDs for later use
            if c_id:
                collected_cycle_ids.add(c_id)

            if emp_id in employee_payroll_map:
                # Add detailed earning record
                employee_payroll_map[emp_id]["earnings"].append({
                    "earning_id": earning_id,
                    "earning_type": earning.get("earning_type"),
                    "amount": amount,
                    "status": earning.get("status"),
                    "created_at": earning.get("created_at"),
                })
                employee_payroll_map[emp_id]["total_earnings_amount"] += amount

        # Process deductions - with detailed records
        for deduction_id, deduction in deductions.items():
            emp_id = deduction.get("employee_id")
            c_id = deduction.get("cycle_id")

            # Apply cycle filter for deductions
            if cycle_id and c_id and c_id != cycle_id:
                continue
            # Apply employee/department filter
            if relevant_employee_ids is not None and emp_id not in relevant_employee_ids:
                continue

            amount = float(deduction.get("amount", 0) or 0)
            total_deductions += amount
            
            # Collect cycle IDs for later use
            if c_id:
                collected_cycle_ids.add(c_id)

            if emp_id in employee_payroll_map:
                # Add detailed deduction record
                deduction_rule_id = deduction.get("deduction_rule_id")
                deduction_rules = data.get("deduction_rules", {})
                deduction_rule = deduction_rules.get(deduction_rule_id, {})
                
                employee_payroll_map[emp_id]["deductions"].append({
                    "deduction_id": deduction_id,
                    "deduction_rule_id": deduction_rule_id,
                    "deduction_type": deduction_rule.get("deduction_type"),
                    "amount": amount,
                    "status": deduction.get("status"),
                    "deduction_date": deduction.get("deduction_date"),
                })
                employee_payroll_map[emp_id]["total_deductions_amount"] += amount

        # Convert map to list
        employee_details = list(employee_payroll_map.values())
        
        # Populate cycle_info when filtering by employee_id or department_id (but not cycle_id)
        # Collect all cycles found in the data
        if not cycle_id and collected_cycle_ids:
            # Build a list of all cycle info for the collected cycles
            cycle_info = []
            for c_id in sorted(collected_cycle_ids):  # Sort for consistent ordering
                cycle = payroll_cycles.get(c_id, {})
                cycle_info.append({
                    "cycle_id": c_id,
                    "start_date": cycle.get("start_date"),
                    "end_date": cycle.get("end_date"),
                    "frequency": cycle.get("frequency"),
                    "status": cycle.get("status"),
                })

        report = {
            "report_type": "payroll_report",
            "generated_at": "2025-11-16T23:59:00",
            "filters": {
                "employee_id": employee_id,
                "cycle_id": cycle_id,
                "department_id": department_id,
            },
            "cycle_info": cycle_info,
            "summary": {
                "total_employees": len(employee_details),
                "total_hours_worked": total_hours_worked,
                "total_overtime_hours": total_overtime_hours,
                "total_earnings": total_earnings,
                "total_deductions": total_deductions,
                "total_net_pay": total_net_pay,
                "net_payroll": total_earnings - total_deductions,
            },
            "employee_details": employee_details,
        }

        return json.dumps(report)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "generate_payroll_report",
                "description": (
                    "Generates a comprehensive payroll report using payroll_cycles, payroll_inputs, "
                    "payslips, earnings, and deductions data. Includes summary statistics and detailed "
                    "employee payroll information including hours worked, detailed earnings (bonuses, commissions), "
                    "detailed deductions, and net pay from payslips. "
                    "At least one of employee_id, cycle_id, or department_id must be provided."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Filter by specific employee ID to get payroll data for a single employee.",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Filter by specific payroll cycle ID to get data for all employees in that cycle.",
                        },
                        "department_id": {
                            "type": "string",
                            "description": "Filter by specific department ID to get data for all employees in that department.",
                        },
                    },
                    "required": [],
                },
            },
        }
