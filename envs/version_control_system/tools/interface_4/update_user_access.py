import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateUserAccess(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        organization_id: str,
        user_id: str,
        auth_token: str,
        role: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        access_tokens = data.get("access_tokens", {})
        organization_members = data.get("organization_members", {})
        organizations = data.get("organizations", {})

        if organization_id not in organizations:
            return json.dumps({"success": False, "error": "Organization not found"})

        def encode(text: str) -> str:
            return base64.b64encode(text.encode("utf-8")).decode("utf-8")

        # --- Authenticate requester ---
        encoded_token = encode(auth_token)
        token_info = next(
            (
                info
                for info in access_tokens.values()
                if info.get("token_encoded") == encoded_token
            ),
            None,
        )

        if not token_info:
            return json.dumps(
                {"success": False, "error": "Invalid authentication token"}
            )

        requester_id = token_info.get("user_id")

        # --- Authorization: requester must be owner ---
        requester_membership = next(
            (
                m
                for m in organization_members.values()
                if m.get("organization_id") == organization_id
                and m.get("user_id") == requester_id
                and m.get("role") == "owner"
                and m.get("status") == "active"
            ),
            None,
        )

        if not requester_membership:
            return json.dumps(
                {
                    "success": False,
                    "error": "Access denied. Organization owner role required.",
                }
            )

        # --- Target membership ---
        target_membership = next(
            (
                m
                for m in organization_members.values()
                if m.get("organization_id") == organization_id
                and m.get("user_id") == user_id
            ),
            None,
        )

        if not target_membership:
            return json.dumps(
                {
                    "success": False,
                    "error": "Target user is not a member of the organization",
                }
            )

        # --- Validate enums ---
        if role and role not in {"owner", "member"}:
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid role. Allowed values: owner, member",
                }
            )

        if status and status not in {"active", "pending", "inactive"}:
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid status. Allowed values: active, pending, inactive",
                }
            )

        # --- Prevent removing last owner ---
        if target_membership.get("role") == "owner" and (
            role == "member" or status == "inactive"
        ):
            active_owners = [
                m
                for m in organization_members.values()
                if m.get("organization_id") == organization_id
                and m.get("role") == "owner"
                and m.get("status") == "active"
            ]

            if len(active_owners) <= 1:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Operation denied. Organization must have at least one active owner.",
                    }
                )

        # --- Apply updates ---
        updated_fields = {}

        if role:
            target_membership["role"] = role
            updated_fields["role"] = role

        if status:
            target_membership["status"] = status
            updated_fields["status"] = status

        return json.dumps(
            {
                "success": True,
                "organization_id": organization_id,
                "user_id": user_id,
                "updated_fields": updated_fields,
                "membership": target_membership,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_user_access",
                "description": (
                    "Updates an organization member's access by changing their role or membership "
                    "status."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "organization_id": {
                            "type": "string",
                            "description": "The organization in which the user's access will be updated.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The target user whose access is being modified.",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "Authentication token of the requesting organization owner.",
                        },
                        "role": {
                            "type": "string",
                            "enum": ["owner", "member"],
                            "description": "Optional new role to assign to the user.",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["active", "pending", "inactive"],
                            "description": (
                                "Optional membership status update. "
                                "Use 'inactive' to revoke access."
                            ),
                        },
                    },
                    "required": ["organization_id", "user_id", "auth_token"],
                },
            },
        }
