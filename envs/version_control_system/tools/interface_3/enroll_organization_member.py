import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class EnrollOrganizationMember(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        organization_id: str,
        user_id: str,
        role: str,
        status: str
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not organization_id:
            return json.dumps({"success": False, "error": "organization_id is required to enroll organization member"})
        if not user_id:
            return json.dumps({"success": False, "error": "user_id is required to enroll organization member"})
        if not role:
            return json.dumps({"success": False, "error": "role is required to enroll organization member"})
        if not status:
            return json.dumps({"success": False, "error": "status is required to enroll organization member"})

        organizations = data.get("organizations", {})
        users = data.get("users", {})
        organization_members = data.get("organization_members", {})

        # Validate organization exists
        if str(organization_id) not in organizations:
            return json.dumps({"success": False, "error": f"Organization with id '{organization_id}' not found"})

        # Validate user exists
        if str(user_id) not in users:
            return json.dumps({"success": False, "error": f"User with id '{user_id}' not found"})

        # Validate role
        valid_roles = ["owner", "member"]
        if role not in valid_roles:
            return json.dumps({"success": False, "error": f"Invalid role '{role}'. Valid values: owner, member"})

        # Validate status
        valid_statuses = ["active", "pending", "inactive"]
        if status not in valid_statuses:
            return json.dumps({"success": False, "error": f"Invalid status '{status}'. Valid values: active, pending, inactive"})

        # Check if user is already a member of this organization
        for membership_id, membership in organization_members.items():
            if (str(membership.get("organization_id")) == str(organization_id) and
                str(membership.get("user_id")) == str(user_id)):
                return json.dumps({"success": False, "error": f"User '{user_id}' is already a member of organization '{organization_id}'"})

        # Generate new membership_id
        if organization_members:
            max_id = max(int(k) for k in organization_members.keys())
            new_id = str(max_id + 1)
        else:
            new_id = "1"

        # Create membership record
        new_membership = {
            "membership_id": new_id,
            "organization_id": organization_id,
            "user_id": user_id,
            "role": role,
            "status": status,
            "joined_at": "2026-01-01T23:59:00"
        }

        organization_members[new_id] = new_membership

        return json.dumps({"success": True, "result": new_membership})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "enroll_organization_member",
                "description": "Adds a user as a member to an organization.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "organization_id": {
                            "type": "string",
                            "description": "The unique identifier of the organization to add the member to."
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The unique identifier of the user to add as a member."
                        },
                        "role": {
                            "type": "string",
                            "description": "The role of the member in the organization. Valid values: owner, member."
                        },
                        "status": {
                            "type": "string",
                            "description": "The membership status. Valid values: active, pending, inactive."
                        }
                    },
                    "required": ["organization_id", "user_id", "role", "status"]
                }
            }
        }