import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ModifyOrganizationMembership(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        membership_id: str,
        role: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """
        Updates an organization membership record with new role or status.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not membership_id:
            return json.dumps({"success": False, "error": "membership_id is required to modify organization membership"})

        if role is None and status is None:
            return json.dumps({"success": False, "error": "At least one of role or status must be provided for update"})

        organization_members = data.get("organization_members", {})

        # Validate membership exists
        if str(membership_id) not in organization_members:
            return json.dumps({"success": False, "error": f"Membership with id '{membership_id}' not found"})

        membership = organization_members[str(membership_id)]

        # Validate and update role if provided
        if role is not None:
            valid_roles = ["owner", "member"]
            if role not in valid_roles:
                return json.dumps({"success": False, "error": f"Invalid role '{role}'. Valid values: owner, member"})
            membership["role"] = role

        # Validate and update status if provided
        if status is not None:
            valid_statuses = ["active", "pending", "inactive"]
            if status not in valid_statuses:
                return json.dumps({"success": False, "error": f"Invalid status '{status}'. Valid values: active, pending, inactive"})
            membership["status"] = status

        return json.dumps({"success": True, "result": membership})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_organization_membership",
                "description": "Updates an organization membership record. Can modify the member's role or status. At least one of role or status must be provided.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "membership_id": {
                            "type": "string",
                            "description": "The unique identifier of the membership record to update."
                        },
                        "role": {
                            "type": "string",
                            "description": "The new role for the member. Valid values: owner, member."
                        },
                        "status": {
                            "type": "string",
                            "description": "The new status for the membership. Valid values: active, pending, inactive."
                        }
                    },
                    "required": ["membership_id"]
                }
            }
        }
