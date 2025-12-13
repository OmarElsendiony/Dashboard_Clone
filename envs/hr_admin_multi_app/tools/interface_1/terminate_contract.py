import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class TerminateContract(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        contract_id: str,
        termination_date: str,
    ) -> str:
        """
        Deletes a contract record from the system.
        """

        if not isinstance(data, dict):
            return json.dumps({"error": "Invalid data format"})

        contracts = data.get("contracts", {})

        # Validate required field
        if not contract_id:
            return json.dumps({
                "error": "Missing required parameter: contract_id"
            })
        
        if not termination_date:
            return json.dumps({
                "error": "Missing required parameter: termination_date"
            })

        # Check if contract exists
        if contract_id not in contracts:
            return json.dumps({
                "error": f"Contract with ID '{contract_id}' not found"
            })

        timestamp = "2025-11-22T12:00:00"
        contract = contracts[contract_id]

        # Update the contract before deletion
        deleted_contract = {
            "contract_id": contract_id,
            "employee_id": contract.get("employee_id"),
            "document_url": contract.get("document_url"),
            "is_terminated": True,
            "termination_date": termination_date,
            "created_at": contract.get("created_at"),
            "last_updated": timestamp
        }

        # Delete the contract
        del contracts[contract_id]

        return json.dumps({
            "success": True,
            "message": f"Contract '{contract_id}' terminated successfully",
            "deleted_contract": deleted_contract
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "terminate_contract",
                "description": "Deletes a contract record from the HR system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "contract_id": {
                            "type": "string",
                            "description": "ID of the contract to delete (required)"
                        },
                        "termination_date": {
                            "type": "string",
                            "description": "Contract termination date in YYYY-MM-DD format (required)"
                        }
                    },
                    "required": ["contract_id", "termination_date"]
                }
            }
        }
