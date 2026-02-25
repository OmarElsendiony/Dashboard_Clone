import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetScopeChangeRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        scope_change_id: Optional[str] = None,
        program_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for scope_changes"
            })
        
        scope_changes = data.get("scope_changes", {})
        
        if not scope_change_id and not program_id and not status:
            return json.dumps({
                "success": False,
                "error": "At least one parameter (scope_change_id, program_id, or status) must be provided"
            })
            
        if status:
            valid_statuses = ["pending_decision", "approved", "rejected"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
                })
        
        if scope_change_id:
            if str(scope_change_id) not in scope_changes:
                return json.dumps({
                    "success": False,
                    "error": f"Scope change request with ID '{scope_change_id}' not found"
                })
            
            scope_change = scope_changes[str(scope_change_id)]
            
            if program_id and str(scope_change.get("project_id")) != str(program_id):
                return json.dumps({
                    "success": False,
                    "error": f"Scope change request does not belong to program '{program_id}'"
                })
            
            if status and str(scope_change.get("status")) != status:
                return json.dumps({
                    "success": False,
                    "error": f"Scope change request status is '{scope_change.get('status')}', not '{status}'"
                })
            
            scope_change_data = {
                "scope_change_id": str(scope_change_id),
                "program_id": str(scope_change.get("project_id", "")) if scope_change.get("project_id") is not None else None,
                "description": str(scope_change.get("description", "")) if scope_change.get("description") is not None else None,
                "requestor_id": str(scope_change.get("requestor_id", "")) if scope_change.get("requestor_id") is not None else None,
                "approver_id": str(scope_change.get("approver_id", "")) if scope_change.get("approver_id") is not None else None,
                "status": str(scope_change.get("status", "")) if scope_change.get("status") is not None else None,
                "submitted_at": str(scope_change.get("submitted_at", "")) if scope_change.get("submitted_at") is not None else None
            }
            
            return json.dumps({
                "success": True,
                "scope_change_data": scope_change_data
            })
        
        if program_id or status:
            found_requests = []
            
            for scid, scope_change in scope_changes.items():
                if program_id and str(scope_change.get("project_id")) != str(program_id):
                    continue
                
                if status and str(scope_change.get("status")) != status:
                    continue
                
                scope_change_data = {
                    "scope_change_id": str(scid),
                    "program_id": str(scope_change.get("project_id", "")) if scope_change.get("project_id") is not None else None,
                    "description": str(scope_change.get("description", "")) if scope_change.get("description") is not None else None,
                    "requestor_id": str(scope_change.get("requestor_id", "")) if scope_change.get("requestor_id") is not None else None,
                    "approver_id": str(scope_change.get("approver_id", "")) if scope_change.get("approver_id") is not None else None,
                    "status": str(scope_change.get("status", "")) if scope_change.get("status") is not None else None,
                    "submitted_at": str(scope_change.get("submitted_at", "")) if scope_change.get("submitted_at") is not None else None
                }
                found_requests.append(scope_change_data)
            
            if not found_requests:
                return json.dumps({
                    "success": False,
                    "error": "No scope change requests found matching the specified filters"
                })
            
            if len(found_requests) == 1:
                return json.dumps({
                    "success": True,
                    "scope_change_data": found_requests[0]
                })
            
            return json.dumps({
                "success": True,
                "count": int(len(found_requests)),
                "scope_changes": found_requests
            })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_scope_change_request",
                "description": "Retrieves scope change request information. Use this to check pending scope changes awaiting decision, review approval status, get scope change details for stakeholder communication, or identify approved changes for implementation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scope_change_id": {
                            "type": "string",
                            "description": "The unique identifier of the scope change request (optional if program_id or status is provided)"
                        },
                        "program_id": {
                            "type": "string",
                            "description": "Filter results by program ID (optional)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter results by status (optional). Valid values: pending_decision, approved, rejected",
                            "enum": ["pending_decision", "approved", "rejected"]
                        }
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["scope_change_id"]},
                        {"required": ["program_id"]},
                        {"required": ["status"]}
                    ]
                }
            }
        }
