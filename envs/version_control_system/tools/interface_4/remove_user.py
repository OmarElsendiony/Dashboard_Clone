import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class RemoveUser(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any], user_id: str, project_id: str, auth_token: str
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        access_tokens = data.get("access_tokens", {})
        projects = data.get("projects", {})
        project_members = data.get("project_members", {})

        def encode(text: str) -> str:
            return base64.b64encode(text.encode("utf-8")).decode("utf-8")

        # --- Authenticate requesting user ---
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

        # --- Validate project ---
        if project_id not in projects:
            return json.dumps(
                {"success": False, "error": f"Project with id {project_id} not found"}
            )

        # --- Validate requester membership ---
        requester_membership = next(
            (
                m_id
                for m_id, m in project_members.items()
                if m.get("user_id") == requester_id
                and m.get("project_id") == project_id
            ),
            None,
        )

        if not requester_membership:
            return json.dumps(
                {
                    "success": False,
                    "error": "User access restricted. Requester is not a member of this project",
                }
            )

        # --- Prevent self-removal ---
        if requester_id == user_id:
            return json.dumps(
                {
                    "success": False,
                    "error": "Users cannot remove themselves from a project",
                }
            )

        # --- Find target membership ---
        target_membership_id = next(
            (
                m_id
                for m_id, m in project_members.items()
                if m.get("user_id") == user_id and m.get("project_id") == project_id
            ),
            None,
        )

        if not target_membership_id:
            return json.dumps(
                {
                    "success": False,
                    "error": "Target user is not a member of the specified project",
                }
            )

        # --- Remove user from project ---
        del project_members[target_membership_id]

        return json.dumps(
            {
                "success": True,
                "message": "User successfully removed from project",
                "removed_user_id": user_id,
                "project_id": project_id,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "remove_user",
                "description": (
                    "Removes a user from a project. "
                    "The requesting user must be authenticated and be a member of the project."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The unique identifier of the user to remove from the project.",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "The unique identifier of the project.",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "Authentication token of the requesting user.",
                        },
                    },
                    "required": ["user_id", "project_id", "auth_token"],
                },
            },
        }
