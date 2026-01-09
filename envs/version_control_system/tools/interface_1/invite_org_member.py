import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class InviteOrgMember(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        organization_id: str,
        user_id: str,
        role: str
    ) -> str:
        """
        Invite a user to an organization.
        """
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
        
        # Check if organization exists
        if organization_id not in organizations:
            return json.dumps({
                "success": False,
                "error": f"Organization with ID '{organization_id}' not found"
            })
        
        # Check if user exists
        if user_id not in users:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{user_id}' not found"
            })
        
        # Validate role
        if role not in ["owner", "member"]:
            return json.dumps({
                "success": False,
                "error": f"Invalid role '{role}'. Must be 'owner' or 'member'"
            })
        
        # Check if requesting user is an owner of the organization
        is_owner = False
        for membership in organization_members.values():
            if (membership.get("organization_id") == organization_id and
                membership.get("user_id") == requesting_user_id and
                membership.get("role") == "owner" and
                membership.get("status") == "active"):
                is_owner = True
                break
        
        if not is_owner:
            return json.dumps({
                "success": False,
                "error": "Insufficient permissions. Only organization owners can invite members"
            })
        
        # Check if user is already a member
        for membership in organization_members.values():
            if (membership.get("organization_id") == organization_id and
                membership.get("user_id") == user_id):
                return json.dumps({
                    "success": False,
                    "error": f"User is already a member of this organization"
                })
        
        timestamp = "2026-01-01T23:59:00"
        new_membership_id = generate_id(organization_members)
        
        new_membership = {
            "membership_id": new_membership_id,
            "organization_id": organization_id,
            "user_id": user_id,
            "role": role,
            "status": "active",
            "joined_at": timestamp
        }
        
        organization_members[new_membership_id] = new_membership
        
        return json.dumps({
            "success": True,
            "membership_id": new_membership_id,
            "membership_data": new_membership
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "invite_org_member",
                "description": "Invite a user to join an organization. Requires the requesting user to be an owner of the organization. Creates a new membership with active status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "Access token for authentication (required)"
                        },
                        "organization_id": {
                            "type": "string",
                            "description": "Organization ID to invite the user to (required)"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User ID to invite (required)"
                        },
                        "role": {
                            "type": "string",
                            "description": "Role to assign. Allowed values: 'owner', 'member' (required)"
                        }
                    },
                    "required": ["access_token", "organization_id", "user_id", "role"]
                }
            }
        }

