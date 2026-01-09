import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class RemoveOrgMember(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        organization_id: str,
        user_id: str
    ) -> str:
        """
        Remove a user from an organization.
        """
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
                "error": "Insufficient permissions. Only organization owners can remove members"
            })
        
        # Find the membership to be removed and check if user is an owner
        membership_found = False
        removed_membership_id = None
        user_is_owner = False
        
        for membership_id, membership in organization_members.items():
            if (membership.get("organization_id") == organization_id and
                membership.get("user_id") == user_id and
                membership.get("status") == "active"):
                membership_found = True
                removed_membership_id = membership_id
                user_is_owner = membership.get("role") == "owner"
                break
        
        if not membership_found:
            return json.dumps({
                "success": False,
                "error": f"User is not an active member of this organization"
            })
        
        # If removing an owner, check if there will be at least one owner remaining
        if user_is_owner:
            active_owner_count = 0
            for membership in organization_members.values():
                if (membership.get("organization_id") == organization_id and
                    membership.get("role") == "owner" and
                    membership.get("status") == "active"):
                    active_owner_count += 1
            
            if active_owner_count <= 1:
                return json.dumps({
                    "success": False,
                    "error": "Cannot remove the last owner from the organization. Transfer ownership to another member first"
                })
        
        # Remove the member by setting status to inactive
        organization_members[removed_membership_id]["status"] = "inactive"
        
        return json.dumps({
            "success": True,
            "membership_id": removed_membership_id,
            "message": f"User {user_id} removed from organization {organization_id}"
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "remove_org_member",
                "description": "Remove a user from an organization by setting their membership status to inactive. Requires the requesting user to be an owner of the organization. Cannot remove the last owner - transfer ownership first.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "Access token for authentication (required)"
                        },
                        "organization_id": {
                            "type": "string",
                            "description": "Organization ID to remove the user from (required)"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User ID to remove (required)"
                        }
                    },
                    "required": ["access_token", "organization_id", "user_id"]
                }
            }
        }