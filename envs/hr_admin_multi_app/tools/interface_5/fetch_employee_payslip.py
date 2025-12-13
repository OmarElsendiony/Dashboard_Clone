import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class FetchEmployeePayslip(Tool):
    """
    Retrieve payslip information for an employee.
    - Returns all payslips for a specific employee.
    - Can filter by cycle_id to get payslip for a specific payroll cycle.
    - Can filter by status (draft, released, updated).
    - Returns payslip details including net pay, cycle, and status.
    - Returns an error if the employee doesn't exist.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        cycle_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Return a JSON string:
          {"success": True, "payslips": [...]} on success
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

        payslips_dict = data.get("payslips", {})
        if not isinstance(payslips_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payslips container: expected dict at data['payslips']",
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
        valid_statuses = ["draft", "released", "updated"]
        if status is not None and status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                }
            )

        # Retrieve payslips for the employee
        employee_payslips = []

        for payslip_id, payslip in payslips_dict.items():
            if not isinstance(payslip, dict):
                continue

            payslip_employee_id = str(payslip.get("employee_id", ""))

            # Check if this payslip belongs to the employee
            if payslip_employee_id != employee_id_str:
                continue

            # Filter by cycle_id if provided
            if cycle_id_str is not None:
                payslip_cycle_id = str(payslip.get("cycle_id", ""))
                if payslip_cycle_id != cycle_id_str:
                    continue

            # Filter by status if provided
            if status is not None:
                payslip_status = payslip.get("status")
                if payslip_status != status:
                    continue

            # Add matching payslip
            payslip_copy = payslip.copy()
            employee_payslips.append(payslip_copy)

        # Sort by created_at (most recent first) for better UX
        employee_payslips.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return json.dumps(
            {
                "success": True,
                "payslips": employee_payslips,
                "count": len(employee_payslips),
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
                "name": "fetch_employee_payslip",
                "description": (
                    "Retrieve payslip information for an employee. "
                    "Returns all payslips for the specified employee. "
                    "Can optionally filter by cycle_id to get payslip for a specific payroll cycle. "
                    "Can optionally filter by status (draft, released, updated). "
                    "Returns payslip details including payslip_id, employee_id, cycle_id, "
                    "net_pay_value, status, created_at, and last_updated. "
                    "Returns an error if the employee doesn't exist."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "The employee ID to retrieve payslips for.",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Optional. Filter payslips by specific cycle ID.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional. Filter payslips by status. Valid values: 'draft', 'released', 'updated'."
                        },
                    },
                    "required": ["employee_id"],
                },
            },
        }
