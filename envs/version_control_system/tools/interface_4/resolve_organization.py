import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool
import base64


class ResolveOrganization(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], organization_name: str, auth_token: str) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        access_tokens = data.get("access_tokens", {})
        orgs = data.get("organizations", {})
        orgs_membership = data.get("organization_members", {})

        def encode(text):
            text_bytes = text.encode("utf-8")
            encoded_bytes = base64.b64encode(text_bytes)
            return encoded_bytes.decode("utf-8")

        encoded_token = encode(auth_token)
        # validate auth token
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

        # retrieve all organization where the authenticated user is a member.
        user_id = token_info.get("user_id")
        user_orgs = [
            orgs.get(membership["organization_id"])
            for membership in orgs_membership.values()
            if user_id == membership["user_id"]
        ]
        target_org = next(
            (org for org in user_orgs if org["organization_name"] == organization_name),
            None,
        )
        if not target_org:
            return json.dumps({"Success": False, "message": "Organization not found"})
        return json.dumps(
            {
                "Success": True,
                "Organization": target_org,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "resolve_organization",
                "description": "Retrieves information about an organization in the version control system using the organization name and requesting user authentication token.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "organization_name": {
                            "type": "string",
                            "description": "The name of the organization to be retrieved.",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "The authentication token of the requesting user.",
                        },
                    },
                    "required": ["organization_name", "auth_token"],
                },
            },
        }
