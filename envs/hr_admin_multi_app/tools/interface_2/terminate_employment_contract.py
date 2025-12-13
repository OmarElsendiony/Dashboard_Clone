import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class TerminateEmploymentContract(Tool):
    """
    Terminate employment contract for an employee.
    Marks the contract as terminated and sets the termination date.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        contract_id: Optional[str] = None,
        employee_id: Optional[str] = None,
    ) -> str:
        """
        Terminate an employment contract.
        
        Args:
            data: Dictionary containing contracts and employees
            contract_id: ID of the contract to terminate (optional, but at least one identifier required)
            employee_id: ID of the employee (optional, but at least one identifier required)
            
        Returns:
            JSON string with success status and updated contract details
        """
        
        timestamp = "2025-11-16T23:59:00"
        termination_date = "2025-12-12"
        
        # Validate data format
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format: 'data' must be a dict"}
            )
        
        contracts = data.get("contracts", {})
        if not isinstance(contracts, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid contracts container: expected dict at data['contracts']",
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
        
        # Validate at least one identifier is provided
        if not contract_id and not employee_id:
            return json.dumps(
                {"success": False, "error": "At least one of contract_id or employee_id is required"}
            )
        
        # Find contract by provided identifier(s)
        contract = None
        contract_id_str = None
        
        if contract_id:
            contract_id_str = str(contract_id)
            if contract_id_str in contracts:
                contract = contracts[contract_id_str]
        
        # If not found by contract_id, try employee_id
        if not contract and employee_id:
            employee_id_str = str(employee_id)
            for c_id, c in contracts.items():
                if c.get("employee_id") == employee_id_str:
                    contract = c
                    contract_id_str = c_id
                    break
        
        # If contract not found with any identifier
        if not contract:
            identifiers = []
            if contract_id:
                identifiers.append(f"contract_id='{contract_id}'")
            if employee_id:
                identifiers.append(f"employee_id='{employee_id}'")
            return json.dumps(
                {
                    "success": False,
                    "error": f"Contract not found with provided identifiers: {', '.join(identifiers)}",
                }
            )
        
        contract_employee_id = contract.get("employee_id")
        
        # If both identifiers provided, validate they match
        if contract_id and employee_id:
            employee_id_str = str(employee_id)
            if contract_employee_id != employee_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Employee ID mismatch: contract '{contract_id_str}' belongs to employee '{contract_employee_id}', not '{employee_id_str}'",
                    }
                )
        
        # Get employee details if available
        employee_name = "Unknown"
        if contract_employee_id and contract_employee_id in employees:
            employee_name = employees[contract_employee_id].get("full_name", "Unknown")
        
        # Check if already terminated
        was_already_terminated = contract.get("is_terminated", False)
        old_termination_date = contract.get("termination_date")
        
        # Update contract to mark as terminated
        contract["is_terminated"] = True
        contract["termination_date"] = termination_date
        contract["last_updated"] = timestamp
        
        if was_already_terminated:
            message = (
                f"Employment contract '{contract_id_str}' for employee '{employee_name}' ({contract_employee_id}) "
                f"was already terminated on {old_termination_date}. Termination date updated to {termination_date}."
            )
        else:
            message = (
                f"Employment contract '{contract_id_str}' for employee '{employee_name}' ({contract_employee_id}) "
                f"has been successfully terminated. Termination date: {termination_date}."
            )
        
        return json.dumps(
            {
                "success": True,
                "message": message,
                "contract": contract,
                "contract_id": contract_id_str,
                "employee_id": contract_employee_id,
                "is_terminated": True,
                "termination_date": termination_date,
                "was_already_terminated": was_already_terminated,
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
                "name": "terminate_employment_contract",
                "description": (
                    "Terminate an employee's employment contract. "
                    "This tool marks the contract as terminated (is_terminated: true) and sets the termination date. "
                    "Can identify the contract by contract_id or employee_id (at least one required). "
                    "Since each employee has exactly one contract, you can use employee_id to find and terminate the contract. "
                    "Used during the employee exit settlement process after the employee account has been disabled. "
                    "Part of the final steps in the offboarding workflow: after exit clearance is completed, "
                    "settlement is paid, employee account is disabled, the employment contract is terminated, "
                    "and then exit documents are archived. "
                    "Each employee has one contract record that can be terminated."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "contract_id": {
                            "type": "string",
                            "description": "ID of the contract to terminate (optional, but at least one identifier required)",
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "ID of the employee (optional, but at least one identifier required). Since each employee has one contract, this can be used to find and terminate the contract.",
                        },
                    },
                    "required": [],
                },
            },
        }

