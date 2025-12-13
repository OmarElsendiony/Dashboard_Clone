import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class FetchEmployeeDeductions(Tool):
    """
    Retrieve deduction information for an employee.
    - Returns all deductions for a specific employee.
    - Can filter by cycle_id to get deductions for a specific payroll cycle.
    - Can filter by status (valid, invalid_limit_exceeded).
    - Can filter by deduction_code.
    - Returns deduction details including amount, rule, and status.
    - Returns an error if the employee doesn't exist.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        cycle_id: Optional[str] = None,
        status: Optional[str] = None,
        deduction_code: Optional[str] = None,
    ) -> str:
        """
        Return a JSON string:
          {"success": True, "deductions": [...]} on success
          {"success": False, "error": "..."} on error
        """

        # Basic input validation
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        employees_dict = data.get("employees", {})
        if not isinstance(employees_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid employees container: expected dict at data['employees']",
                }
            )

        deductions_dict = data.get("deductions", {})
        if not isinstance(deductions_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid deductions container: expected dict at data['deductions']",
                }
            )

        deduction_rules_dict = data.get("deduction_rules", {})
        if not isinstance(deduction_rules_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid deduction_rules container: expected dict at data['deduction_rules']",
                }
            )

        # Validate employee_id is provided
        if not employee_id:
            return json.dumps({"success": False, "error": "employee_id is required"})

        # Convert employee_id to string for consistent comparison
        employee_id_str = str(employee_id)

        # Check if employee exists
        if employee_id_str not in employees_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id_str}' not found",
                }
            )

        # Convert cycle_id to string if provided
        cycle_id_str = str(cycle_id) if cycle_id is not None else None

        # Validate status if provided
        valid_statuses = ["valid", "invalid_limit_exceeded"]
        if status is not None and status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                }
            )

        # Validate deduction_code if provided
        valid_deduction_codes = [
            "benefit_contribution", "repayment_of_overpayment", "loan",
            "retirement", "insurance", "tax", "garnishment"
        ]
        if deduction_code is not None and deduction_code not in valid_deduction_codes:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid deduction_type '{deduction_code}'. Must be one of: {', '.join(valid_deduction_codes)}",
                }
            )

        # Retrieve deductions for the employee
        employee_deductions = []

        for deduction_id, deduction in deductions_dict.items():
            if not isinstance(deduction, dict):
                continue

            deduction_employee_id = str(deduction.get("employee_id", ""))
            
            # Check if this deduction belongs to the employee
            if deduction_employee_id != employee_id_str:
                continue

            # Filter by cycle_id if provided
            if cycle_id_str is not None:
                deduction_cycle_id = deduction.get("cycle_id")
                if deduction_cycle_id is not None:
                    if str(deduction_cycle_id) != cycle_id_str:
                        continue

            # Filter by status if provided
            if status is not None:
                deduction_status = deduction.get("status")
                if deduction_status != status:
                    continue

            # Filter by deduction_code if provided (get from deduction_rule)
            if deduction_code:
                deduction_rule_id = deduction.get("deduction_rule_id")
                if deduction_rule_id:
                    deduction_rule = deduction_rules_dict.get(str(deduction_rule_id))
                    if isinstance(deduction_rule, dict):
                        rule_deduction_type = deduction_rule.get("deduction_type")
                        if rule_deduction_type != deduction_code:
                            continue
                    else:
                        continue
                else:
                    continue

            # Add matching deduction
            deduction_copy = deduction.copy()
            employee_deductions.append(deduction_copy)

        # Sort by deduction_date (most recent first) for better UX
        employee_deductions.sort(
            key=lambda x: x.get("deduction_date", ""), 
            reverse=True
        )

        return json.dumps(
            {
                "success": True,
                "deductions": employee_deductions,
                "count": len(employee_deductions),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """
        Tool schema for function-calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "fetch_employee_deductions",
                "description": (
                    "Retrieve deduction information for an employee. "
                    "Returns all deductions for the specified employee. "
                    "Can optionally filter by cycle_id to get deductions for a specific payroll cycle. "
                    "Can optionally filter by status (valid, invalid_limit_exceeded). "
                    "Can optionally filter by deduction_code (benefit_contribution, repayment_of_overpayment, "
                    "loan, retirement, insurance, tax, garnishment). "
                    "Returns deduction details including deduction_id, employee_id, cycle_id, "
                    "deduction_rule_id, amount, deduction_date, status, created_at, and last_updated. "
                    "Returns an error if the employee doesn't exist."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The employee ID to retrieve deductions for.",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Optional. Filter deductions by specific cycle ID.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional. Filter deductions by status. Accepted values: 'valid', 'invalid_limit_exceeded'."
                        },
                        "deduction_code": {
                            "type": "string",
                            "description": "Optional. Filter deductions by type. Accepterf values: 'benefit_contribution', 'repayment_of_overpayment', 'loan', 'retirement', 'insurance', 'tax', 'garnishment'."
                        }
                    },
                    "required": ["employee_id"],
                },
            },
        }