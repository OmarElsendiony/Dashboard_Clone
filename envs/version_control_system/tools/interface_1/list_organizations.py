import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ListOrganizations(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        organization_name: Optional[str] = None,
        visibility: Optional[str] = None,
        plan_type: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for organizations"
            })
        
        # Validate visibility if provided
        if visibility and visibility not in ["public", "limited", "private"]:
            return json.dumps({
                "success": False,
                "error": f"Invalid visibility '{visibility}'. Must be 'public', 'limited', or 'private'"
            })
        
        # Validate plan_type if provided
        if plan_type and plan_type not in ["free", "team", "enterprise"]:
            return json.dumps({
                "success": False,
                "error": f"Invalid plan_type '{plan_type}'. Must be 'free', 'team', or 'enterprise'"
            })
        
        organizations = data.get("organizations", {})
        results = []
        
        for org_id, org_data in organizations.items():
            # Apply filters
            if organization_name and org_data.get("organization_name") != organization_name:
                continue
            if visibility and org_data.get("visibility") != visibility:
                continue
            if plan_type and org_data.get("plan_type") != plan_type:
                continue
            if organization_id and org_id != organization_id:
                continue
            
            results.append({**org_data, "organization_id": org_id})
        
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
                "name": "list_organizations",
                "description": "Lists organizations with optional filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "organization_name": {
                            "type": "string",
                            "description": "Filter by organization name (exact match) (optional)"
                        },
                        "visibility": {
                            "type": "string",
                            "description": "Filter by visibility. Allowed values: 'public', 'limited', 'private' (optional)",
                            "enum" : ["public", "limited", "private"]
                        },
                        "plan_type": {
                            "type": "string",
                            "description": "Filter by plan type. Allowed values: 'free', 'team', 'enterprise' (optional)",
                            "enum" : ["free", "team", "enterprise"]
                        },
                        "organization_id": {
                            "type": "string",
                            "description": "Filter by organization_id (exact match) (optional)"
                        }
                    },
                    "required": []
                }
            }
        }

