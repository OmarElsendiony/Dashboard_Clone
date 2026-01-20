import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool
import base64


class SetPermission(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any], permission_config: Dict[str, Any], auth_token: str
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not permission_config:
            return json.dumps(
                {
                    "success": False,
                    "message": "Permission configuration must be provided.",
                }
            )

        access_tokens = data.get("access_tokens", {})
        orgs = data.get("organizations", {})

        def encode(text):
            text_bytes = text.encode("utf-8")
            encoded_bytes = base64.b64encode(text_bytes)
            return encoded_bytes.decode("utf-8")

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

        allowed_visibilities = {"public", "limited", "private"}

        target_organization_id = permission_config.get("organization_id")
        if not target_organization_id:
            return json.dumps(
                {"success": False, "message": "Organization_id not provided."}
            )

        target_org = orgs.get(target_organization_id)
        if not target_org:
            return json.dumps({"success": False, "message": "Organization not found."})

        visibility = permission_config.get("visibility")
        if not visibility:
            return json.dumps({"success": False, "message": "visibility not provided."})

        if visibility not in allowed_visibilities:
            return json.dumps(
                {
                    "success": False,
                    "message": f"Invalid visibility. Allowed values {sorted(allowed_visibilities)}",
                }
            )

        target_org["visibility"] = visibility

        return json.dumps({"success": True, "organization": target_org})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "set_permission",
                "description": (
                    "Updates the visibility setting of an existing organization. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "auth_token": {
                            "type": "string",
                            "description": (
                                "Authentication token of the requesting user. "
                                "The token is validated against the system's access token registry "
                                "before any permission changes are applied."
                            ),
                        },
                        "permission_config": {
                            "type": "object",
                            "description": (
                                "Configuration object describing the permission update to apply. "
                            ),
                            "properties": {
                                "organization_id": {
                                    "type": "string",
                                    "description": (
                                        "Unique identifier of the organization whose visibility "
                                        "setting should be updated."
                                    ),
                                },
                                "visibility": {
                                    "type": "string",
                                    "description": (
                                        "New visibility value to apply to the organization. "
                                        "Accepted values are 'public', 'limited', and 'private'."
                                    ),
                                },
                            },
                            "required": ["organization_id", "visibility"],
                        },
                    },
                    "required": ["auth_token", "permission_config"],
                },
            },
        }
