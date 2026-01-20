import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class FetchOrganizationMembership(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        organization_id: str,
        user_id: str,
        role: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not organization_id:
            return json.dumps({"success": False, "error": "organization_id is required to fetch organization membership"})
        if not user_id:
            return json.dumps({"success": False, "error": "user_id is required to fetch organization membership"})

        organization_members = data.get("organization_members", {})

        # Search for membership record
        found_membership = None
        for membership_id, membership in organization_members.items():
            if (str(membership.get("organization_id")) == str(organization_id) and
                str(membership.get("user_id")) == str(user_id)):
                found_membership = membership
                break

        if not found_membership:
            return json.dumps({"success": False, "error": f"Membership not found for user '{user_id}' in organization '{organization_id}'"})

        # Apply optional role filter
        if role is not None and found_membership.get("role") != role:
            return json.dumps({"success": False, "error": f"Membership exists but role is '{found_membership.get('role')}', not '{role}'"})

        # Apply optional status filter
        if status is not None and found_membership.get("status") != status:
            return json.dumps({"success": False, "error": f"Membership exists but status is '{found_membership.get('status')}', not '{status}'"})

        return json.dumps({"success": True, "result": found_membership})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_organization_membership",
                "description": "Retrieves membership details for a user in an organization.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "organization_id": {
                            "type": "string",
                            "description": "The unique identifier of the organization."
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The unique identifier of the user whose membership to retrieve."
                        },
                        "role": {
                            "type": "string",
                            "description": "Optional filter by role; allowed values: owner, member (optional)."
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional filter by status; allowed values: active, pending, inactive (optional)."
                        }
                    },
                    "required": ["organization_id", "user_id"]
                }
            }
        }
