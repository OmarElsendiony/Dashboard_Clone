import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ComputeExitSettlement(Tool):
    """
    Compute and create exit settlement for an employee.
    Updates exit clearance status to 'cleared' and creates a finance settlement record.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        settlement_amount: float,
        exit_case_id: str,
        cycle_id: Optional[str] = None,
    ) -> str:
        """
        Compute and create exit settlement for an employee.
        
        Args:
            data: Dictionary containing employees, exit_cases, and finance_settlements
            employee_id: ID of the employee (required)
            settlement_amount: Settlement amount to be paid (required)
            exit_case_id: ID of the exit case (required)
            cycle_id: Optional payroll cycle ID for settlement processing
            
        Returns:
            JSON string with success status and settlement details
        """
        
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        timestamp = "2025-12-12T12:00:00"
        
        # Validate data format
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format: 'data' must be a dict"}
            )
        
        employees = data.get("employees", {})
        if not isinstance(employees, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid employees container: expected dict at data['employees']",
                }
            )
        
        exit_cases = data.get("exit_cases", {})
        if not isinstance(exit_cases, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid exit_cases container: expected dict at data['exit_cases']",
                }
            )
        
        finance_settlements = data.get("finance_settlements", {})
        if not isinstance(finance_settlements, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid finance_settlements container: expected dict at data['finance_settlements']",
                }
            )
        
        # Validate required fields
        if not employee_id:
            return json.dumps(
                {"success": False, "error": "employee_id is required"}
            )
        
        if not exit_case_id:
            return json.dumps(
                {"success": False, "error": "exit_case_id is required"}
            )
        
        if settlement_amount is None:
            return json.dumps(
                {"success": False, "error": "settlement_amount is required"}
            )
        
        employee_id_str = str(employee_id)
        exit_case_id_str = str(exit_case_id)
        
        # Validate employee exists
        if employee_id_str not in employees:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee with ID '{employee_id_str}' not found",
                }
            )
        
        employee = employees[employee_id_str]
        
        # Validate exit case exists
        if exit_case_id_str not in exit_cases:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Exit case with ID '{exit_case_id_str}' not found",
                }
            )
        
        exit_case = exit_cases[exit_case_id_str]
        
        # Validate exit case belongs to the employee
        if exit_case.get("employee_id") != employee_id_str:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Exit case '{exit_case_id_str}' does not belong to employee '{employee_id_str}'",
                }
            )
        
        # Validate settlement amount is non-negative
        try:
            amount_value = float(settlement_amount)
            if amount_value < 0:
                return json.dumps(
                    {
                        "success": False,
                        "error": "settlement_amount must be non-negative",
                    }
                )
        except (ValueError, TypeError):
            return json.dumps(
                {
                    "success": False,
                    "error": "settlement_amount must be a valid number",
                }
            )
        
        # Check if settlement already exists for this employee
        existing_settlement = None
        for settlement in finance_settlements.values():
            if settlement.get("employee_id") == employee_id_str:
                existing_settlement = settlement
                break
        
        if existing_settlement:
            # Update existing settlement
            settlement_id = existing_settlement.get("settlement_id")
            existing_settlement["amount"] = str(amount_value)
            existing_settlement["is_cleared"] = False
            existing_settlement["last_updated"] = timestamp
            
            settlement_record = existing_settlement
            action = "updated"
        else:
            # Create new settlement
            settlement_id = generate_id(finance_settlements)
            
            new_settlement = {
                "settlement_id": settlement_id,
                "employee_id": employee_id_str,
                "amount": str(amount_value),
                "is_cleared": False,
                "created_at": timestamp,
                "last_updated": timestamp,
            }
            
            finance_settlements[settlement_id] = new_settlement
            settlement_record = new_settlement
            action = "created"
        
        # Update exit case clearance status to 'cleared'
        old_status = exit_case.get("exit_clearance_status")
        exit_case["exit_clearance_status"] = "cleared"
        exit_case["last_updated"] = timestamp
        
        return json.dumps(
            {
                "success": True,
                "message": f"Exit settlement {action} for employee '{employee.get('full_name')}' ({employee_id_str}). "
                          f"Exit clearance status updated from '{old_status}' to 'cleared'. "
                          f"Settlement amount: ${amount_value:.2f}",
                "settlement": settlement_record,
                "exit_case": exit_case,
                "settlement_id": settlement_id,
                "exit_case_id": exit_case_id_str,
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
                "name": "compute_exit_settlement",
                "description": (
                    "Compute and create exit settlement for an employee leaving the organization. "
                    "This tool performs two key actions: "
                    "1) Creates or updates a finance settlement record with the specified settlement amount "
                    "2) Updates the exit case clearance status to 'cleared'. "
                    "Used in both Exit Clearance Processing (to mark clearance as complete) and "
                    "Exit Settlement Processing (to calculate and record final settlement amount). "
                    "The settlement amount represents the final financial settlement owed to or by the employee, "
                    "which may include unused leave balance, final salary, deductions, etc. "
                    "The settlement is initially marked as 'is_cleared: false' until payment is processed."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "ID of the employee (required)",
                        },
                        "settlement_amount": {
                            "type": "number",
                            "description": "Settlement amount to be paid (required, must be non-negative)",
                        },
                        "exit_case_id": {
                            "type": "string",
                            "description": "ID of the exit case (required)",
                        },
                        "cycle_id": {
                            "type": "string",
                            "description": "Optional payroll cycle ID for settlement processing",
                        },
                    },
                    "required": ["employee_id", "settlement_amount", "exit_case_id"],
                },
            },
        }

