import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class UpdateScopeChangeRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        scope_change_id: str,
        status: str,
        approver_id: str
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for scope_changes"
            })
        
        scope_changes = data.get("scope_changes", {})
        users = data.get("users", {})
        
        if not all([scope_change_id, status, approver_id]):
            return json.dumps({
                "success": False,
                "error": "Missing required parameters: scope_change_id, status, and approver_id are required"
            })
        
        if str(scope_change_id) not in scope_changes:
            return json.dumps({
                "success": False,
                "error": f"Scope change request with ID '{scope_change_id}' not found"
            })
        
        scope_change = scope_changes[str(scope_change_id)]
        
        if str(approver_id) not in users:
            return json.dumps({
                "success": False,
                "error": f"Approver with user_id '{approver_id}' not found"
            })
        
        valid_statuses = ["pending_decision", "approved", "rejected"]
        if status not in valid_statuses:
            return json.dumps({
                "success": False,
                "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
            })
        
        updated_scope_change = scope_change.copy()
        updated_scope_change["status"] = str(status)
        updated_scope_change["approver_id"] = str(approver_id)
        
        scope_changes[str(scope_change_id)] = updated_scope_change
        
        scope_change_response = {
            "scope_change_id": str(scope_change_id),
            "program_id": str(updated_scope_change.get("project_id", "")) if updated_scope_change.get("project_id") is not None else None,
            "description": str(updated_scope_change.get("description", "")) if updated_scope_change.get("description") is not None else None,
            "requestor_id": str(updated_scope_change.get("requestor_id", "")) if updated_scope_change.get("requestor_id") is not None else None,
            "approver_id": str(updated_scope_change.get("approver_id", "")) if updated_scope_change.get("approver_id") is not None else None,
            "status": str(updated_scope_change.get("status", "")) if updated_scope_change.get("status") is not None else None,
            "submitted_at": str(updated_scope_change.get("submitted_at", "")) if updated_scope_change.get("submitted_at") is not None else None
        }
        
        return json.dumps({
            "success": True,
            "message": f"Scope change request '{scope_change_id}' updated successfully",
            "scope_change_id": str(scope_change_id),
            "scope_change_data": scope_change_response
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_scope_change_request",
                "description": "Approves or rejects a scope change request. Use this when making scope change decisions, recording formal approvals from leadership, documenting scope change outcomes, or finalizing scope modification decisions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scope_change_id": {
                            "type": "string",
                            "description": "The ID of the scope change request to update"
                        },
                        "status": {
                            "type": "string",
                            "description": "New scope change request status.",
                            "enum": ["approved", "rejected", "pending_decision"]
                        },
                        "approver_id": {
                            "type": "string",
                            "description": "User ID of the approver"
                        }
                    },
                    "required": ["scope_change_id", "status", "approver_id"]
                }
            }
        }
