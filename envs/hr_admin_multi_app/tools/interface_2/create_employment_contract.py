import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class CreateEmploymentContract(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_info: Dict[str, str],
    ) -> str:
        """
        Create an employment contract for a worker (employee).
        
        Args:
            data: Environment data containing contracts and employees
            employee_info: Dictionary containing employee_id and document_url
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        
        contracts = data.get("contracts", {})
        employees = data.get("employees", {})
        
        # Validate employee_info structure
        if not isinstance(employee_info, dict):
            return json.dumps({
                "success": False,
                "error": "employee_info must be a dictionary"
            })
        
        employee_id = employee_info.get("employee_id")
        document_url = employee_info.get("document_url")
        
        # Validate required fields
        if not employee_id:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: employee_id in employee_info"
            })
        
        if not document_url:
            return json.dumps({
                "success": False,
                "error": "Missing required parameter: document_url in employee_info"
            })
        
        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"Employee with ID '{employee_id}' not found"
            })
        
        # Generate new contract ID
        def generate_contract_id(contracts: Dict[str, Any]) -> str:
            if not contracts:
                return "1"
            try:
                max_id = max(int(k) for k in contracts.keys() if k.isdigit())
                return str(max_id + 1)
            except ValueError:
                # If no numeric keys, start from 1
                return "1"
        
        new_contract_id = generate_contract_id(contracts)
        
        # Use the specified timestamp
        current_time = "2025-12-12T12:00:00"
        
        # Create new contract
        new_contract = {
            "contract_id": new_contract_id,
            "employee_id": str(employee_id),
            "document_url": str(document_url),
            "created_at": current_time,
            "is_terminated": False,
            "termination_date": None,
            "last_updated": current_time
        }
        
        # Add contract to data
        contracts[new_contract_id] = new_contract
        
        # Return the created contract
        return json.dumps({
            "success": True,
            "contract": new_contract
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_employment_contract",
                "description": "Create an employment contract for a worker (employee). Requires employee_info containing employee_id and document_url. Returns the created contract with contract_id, employee_id, document_url, created_at, is_terminated, termination_date, and last_updated.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_info": {
                            "type": "object",
                            "description": "Dictionary containing employee_id (string) and document_url (string)",
                            "properties": {
                                "employee_id": {
                                    "type": "string",
                                    "description": "ID of the employee (worker) to create a contract for"
                                },
                                "document_url": {
                                    "type": "string",
                                    "description": "URL of the contract document"
                                }
                            },
                            "required": ["employee_id", "document_url"]
                        }
                    },
                    "required": ["employee_info"]
                }
            }
        }

