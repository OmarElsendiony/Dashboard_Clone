import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ReleasePayslip(Tool):
    """
    Release a payslip by changing its status to 'released'.
    Used to finalize and release payslips to employees.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        payslip_id: str,
        employee_id: Optional[str] = None,
        cycle_id: Optional[str] = None,
    ) -> str:
        """
        Release a payslip by updating its status to 'released'.
        
        Args:
            data: Dictionary containing payslips, employees, and payroll_cycles
            payslip_id: ID of the payslip (required)
            employee_id: Optional employee ID for validation
            cycle_id: Optional cycle ID for validation
            
        Returns:
            JSON string with success status and updated payslip details
        """
        
        # Validate data format
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format: 'data' must be a dict"}
            )
        
        payslips = data.get("payslips", {})
        if not isinstance(payslips, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payslips container: expected dict at data['payslips']",
                }
            )
        
        employees = data.get("employees", {})
        if not isinstance(employees, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid employees container: expected dict at data['employees']",
                }
            )
        
        payroll_cycles = data.get("payroll_cycles", {})
        if not isinstance(payroll_cycles, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid payroll_cycles container: expected dict at data['payroll_cycles']",
                }
            )
        
        # Validate required fields
        if not payslip_id:
            return json.dumps(
                {"success": False, "error": "payslip_id is required"}
            )
        
        payslip_id_str = str(payslip_id)
        
        # Validate payslip exists
        if payslip_id_str not in payslips:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payslip with ID '{payslip_id_str}' not found",
                }
            )
        
        payslip = payslips[payslip_id_str]
        
        # Optional validation: verify employee_id matches if provided
        if employee_id:
            employee_id_str = str(employee_id)
            if payslip.get("employee_id") != employee_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Payslip '{payslip_id_str}' does not belong to employee '{employee_id_str}'. It belongs to employee '{payslip.get('employee_id')}'.",
                    }
                )
            
            # Validate employee exists
            if employee_id_str not in employees:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Employee with ID '{employee_id_str}' not found",
                    }
                )
        
        # Optional validation: verify cycle_id matches if provided
        if cycle_id:
            cycle_id_str = str(cycle_id)
            if payslip.get("cycle_id") != cycle_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Payslip '{payslip_id_str}' does not belong to cycle '{cycle_id_str}'. It belongs to cycle '{payslip.get('cycle_id')}'.",
                    }
                )
            
            # Validate cycle exists
            if cycle_id_str not in payroll_cycles:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Payroll cycle with ID '{cycle_id_str}' not found",
                    }
                )
        
        current_status = payslip.get("status")
        
        # Check if already released
        if current_status == "released":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payslip '{payslip_id_str}' is already released. Cannot release again.",
                }
            )
        
        # Validate current status is draft or updated
        valid_release_statuses = ["draft", "updated"]
        if current_status not in valid_release_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Payslip '{payslip_id_str}' has status '{current_status}'. Can only release payslips with status 'draft' or 'updated'.",
                }
            )
        
        timestamp = "2025-11-16T23:59:00"
        
        # Update payslip status to released
        payslip["status"] = "released"
        payslip["last_updated"] = timestamp
        
        return json.dumps(
            {
                "success": True,
                "message": f"Payslip '{payslip_id_str}' has been released successfully for employee '{payslip.get('employee_id')}' in cycle '{payslip.get('cycle_id')}'",
                "payslip": payslip,
                "previous_status": current_status,
                "action": "released",
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
                "name": "release_payslip",
                "description": (
                    "Release a payslip by updating its status to 'released'. "
                    "Validates that the payslip exists and is not already released. "
                    "Only payslips with status 'draft' or 'updated' can be released. "
                    "Optional employee_id and cycle_id parameters can be provided for additional validation "
                    "to ensure the payslip belongs to the expected employee and cycle. "
                    "This is the final step in the payslip lifecycle before the payslip is made available to the employee. "
                    "After release, the payslip status cannot be changed back."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payslip_id": {
                            "type": "string",
                            "description": "ID of the payslip to release (required)",
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "Optional: Employee ID for validation. If provided, verifies the payslip belongs to this employee.",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Optional: Cycle ID for validation. If provided, verifies the payslip belongs to this cycle.",
                        },
                    },
                    "required": ["payslip_id"],
                },
            },
        }

