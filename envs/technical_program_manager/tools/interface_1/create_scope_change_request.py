import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class CreateScopeChangeRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        program_id: str,
        description: str,
        requestor_id: str
    ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(int(max(table.keys(), key=lambda x: int(x))) + 1)
        
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for scope_changes"
            })
        
        scope_changes = data.get("scope_changes", {})
        projects = data.get("projects", {})
        users = data.get("users", {})
        
        if not all([program_id, description, requestor_id]):
            return json.dumps({
                "success": False,
                "error": "Missing required parameters: program_id, description, and requestor_id are required"
            })
        
        if str(program_id) not in projects:
            return json.dumps({
                "success": False,
                "error": f"Project with ID '{program_id}' not found"
            })
        
        if str(requestor_id) not in users:
            return json.dumps({
                "success": False,
                "error": f"Requestor with user_id '{requestor_id}' not found"
            })
        
        new_scope_change_id = generate_id(scope_changes)
        
        new_scope_change = {
            "scope_change_id": str(new_scope_change_id),
            "project_id": str(program_id),
            "description": str(description),
            "requestor_id": str(requestor_id),
            "approver_id": None,
            "status": "pending_decision",
            "submitted_at": "2026-02-11T23:59:00"
        }
        
        scope_changes[str(new_scope_change_id)] = new_scope_change
        
        scope_change_response = {
            "scope_change_id": str(new_scope_change_id),
            "program_id": str(program_id),
            "description": str(description),
            "requestor_id": str(requestor_id),
            "approver_id": None,
            "status": "pending_decision",
            "submitted_at": "2026-02-11T23:59:00"
        }
        
        return json.dumps({
            "success": True,
            "message": "Scope change request created successfully",
            "scope_change_id": str(new_scope_change_id),
            "scope_change_data": scope_change_response
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_scope_change_request",
                "description": "Submits a new scope change request. Use this when program scope needs modification, new requirements emerge from stakeholders, scope adjustments are needed due to constraints, or formal approval is required for scope expansion or reduction.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "program_id": {
                            "type": "string",
                            "description": "Project ID the scope change belongs to (required, must exist)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Scope change description (required)"
                        },
                        "requestor_id": {
                            "type": "string",
                            "description": "User ID of the requestor (required, must exist)"
                        }
                    },
                    "required": ["program_id", "description", "requestor_id"]
                }
            }
        }
