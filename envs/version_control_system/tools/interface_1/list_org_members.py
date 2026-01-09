import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ListOrgMembers(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        organization_id: Optional[str] = None,
        role: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """
        List organization members with optional filters.
        """
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for organization members"
            })
        
        # Validate role if provided
        if role and role not in ["owner", "member"]:
            return json.dumps({
                "success": False,
                "error": f"Invalid role '{role}'. Must be 'owner' or 'member'"
            })
        
        # Validate status if provided
        if status and status not in ["active", "pending", "inactive"]:
            return json.dumps({
                "success": False,
                "error": f"Invalid status '{status}'. Must be 'active', 'pending', or 'inactive'"
            })
        
        organization_members = data.get("organization_members", {})
        results = []
        
        for member_id, member_data in organization_members.items():
            # Apply filters
            if organization_id and member_data.get("organization_id") != organization_id:
                continue
            if role and member_data.get("role") != role:
                continue
            if status and member_data.get("status") != status:
                continue
            
            results.append({**member_data, "membership_id": member_id})
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "results": results
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_org_members",
                "description": "List organization members. Can filter by organization_id, role, or status. Returns all organization members if no filters are provided.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "organization_id": {
                            "type": "string",
                            "description": "Filter by organization_id (exact match)"
                        },
                        "role": {
                            "type": "string",
                            "description": "Filter by role. Allowed values: 'owner', 'member'"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status. Allowed values: 'active', 'pending', 'inactive'"
                        }
                    },
                    "required": []
                }
            }
        }

