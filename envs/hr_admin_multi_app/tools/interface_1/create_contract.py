import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateContract(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str = None,
        document_url: Optional[str] = None
    ) -> str:
        """
        Creates a new contract record for an employee.
        """
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        timestamp = "2025-11-22T12:00:00"
        contracts = data.get("contracts", {})
        employees = data.get("employees", {})

        # Validate required field
        if not employee_id:
            return json.dumps({
                "error": "Missing required parameter: employee_id"
            })

        # Check if employee exists
        if employee_id not in employees:
            return json.dumps({
                "error": f"Employee with ID '{employee_id}' not found"
            })

        # Check if contract already exists for this employee
        for existing_contract in contracts.values():
            if existing_contract.get("employee_id") == employee_id:
                return json.dumps({
                    "error": f"Contract already exists for employee '{employee_id}'"
                })

        # Generate new contract ID
        new_contract_id = generate_id(contracts)

        # Create new contract record
        new_contract = {
            "contract_id": new_contract_id,
            "employee_id": employee_id,
            "document_url": document_url,
            "is_terminated": False,
            "termination_date": None,
            "created_at": timestamp,
            "last_updated": timestamp
        }

        contracts[new_contract_id] = new_contract
    
        return json.dumps(
            {
                "success": True,
                "message": f"Contract {new_contract_id} created successfully",
                "employee_data": new_contract
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_contract",
                "description": "Creates a new contract record for an employee in the HR system. Validates employee existence and ensures one contract per employee. Used for contract management and employment documentation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "ID of the employee (required, must exist in employees table, one contract per employee)"
                        },
                        "document_url": {
                            "type": "string",
                            "description": "URL link to the digital contract document (optional)"
                        }
                    },
                    "required": ["employee_id"]
                }
            }
        }
