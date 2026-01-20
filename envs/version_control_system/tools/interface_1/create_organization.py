import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateOrganization(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        organization_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[str] = None,
        plan_type: Optional[str] = None
    ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        def get_user_from_token(token: str, tokens_data: Dict[str, Any]) -> Optional[str]:
            """Encode token and find associated user_id"""
            try:
                encoded_token = base64.b64encode(token.encode('utf-8')).decode('utf-8')
                for token_info in tokens_data.values():
                    if token_info.get("token_encoded") == encoded_token:
                        return token_info.get("user_id")
                return None
            except:
                return None
        
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })
        
        organizations = data.get("organizations", {})
        organization_members = data.get("organization_members", {})
        users = data.get("users", {})
        access_tokens = data.get("access_tokens", {})
        
        # Validate access token
        requesting_user_id = get_user_from_token(access_token, access_tokens)
        if not requesting_user_id:
            return json.dumps({
                "success": False,
                "error": "Invalid or expired access token"
            })
        
        # Validate user status
        requesting_user = users.get(requesting_user_id)
        if not requesting_user:
            return json.dumps({
                "success": False,
                "error": "User not found"
            })
        
        if requesting_user.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": "User account is not active"
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
        
        # Check for duplicate organization name
        for org in organizations.values():
            if org.get("organization_name") == organization_name:
                return json.dumps({
                    "success": False,
                    "error": f"Organization with name '{organization_name}' already exists"
                })
        
        timestamp = "2026-01-01T23:59:00"
        new_org_id = generate_id(organizations)
        
        new_org = {
            "organization_id": new_org_id,
            "organization_name": organization_name,
            "display_name": display_name,
            "description": description,
            "visibility": visibility if visibility else "private",
            "plan_type": plan_type if plan_type else "free",
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        organizations[new_org_id] = new_org
        
        # Automatically add the creator as an owner
        membership_id = generate_id(organization_members)
        
        new_membership = {
            "membership_id": membership_id,
            "organization_id": new_org_id,
            "user_id": requesting_user_id,
            "role": "owner",
            "status": "active",
            "joined_at": timestamp
        }
        
        organization_members[membership_id] = new_membership
        
        return json.dumps({
            "success": True,
            "action": "create",
            "organization_id": new_org_id,
            "organization_data": new_org,
            "creator_membership": new_membership
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_organization",
                "description": "Creates a new organization. Requires valid access token for authentication",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "Access token for authentication (required)"
                        },
                        "organization_name": {
                            "type": "string",
                            "description": "Name of the organization (required)"
                        },
                        "display_name": {
                            "type": "string",
                            "description": "Display name of the organization (optional)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Organization description (optional)"
                        },
                        "visibility": {
                            "type": "string",
                            "description": "Organization visibility. Allowed values: 'public', 'limited', 'private' (optional, defaults to 'private')",
                            "enum": ["public", "limited", "private"]
                        },
                        "plan_type": {
                            "type": "string",
                            "description": "Plan type. Allowed values: 'free', 'team', 'enterprise' (optional, defaults to 'free')",
                            "enum": ["free", "team", "enterprise"]
                        }
                    },
                    "required": ["access_token", "organization_name"]
                }
            }
        }