import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool
import base64


class AddOrganization(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        organization_name: str,
        auth_token: str,
        description: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        access_tokens = data.get("access_tokens", {})
        orgs = data.get("organizations", {})
        orgs_membership = data.get("organization_members", {})

        def encode(text):
            """
            Encodes text into Base64 format.
            1. Converts string to bytes (.encode).
            2. Encodes bytes to Base64 bytes.
            3. Converts back to string (.decode) for readable output.
            """
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
            orgs[m["organization_id"]]
            for m in orgs_membership.values()
            if m["user_id"] == user_id and m["organization_id"] in orgs
        ]
        if any(org["organization_name"] == organization_name for org in user_orgs):
            return json.dumps(
                {
                    "success": False,
                    "message": f"Organization '{organization_name}' already exists for this user",
                }
            )

        # add new organization
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        new_org_id = generate_id(orgs)
        orgs[new_org_id] = {
            "organization_id": new_org_id,
            "organization_name": organization_name,
            "visibility": "private",
            "display_name": organization_name,
            "description": description,
            "plan_type": "free",
            "created_at": "2026-01-01T23:59:00",
            "updated_at": "2026-01-01T23:59:00",
        }
        # add the user as owner
        new_membership_id = generate_id(orgs_membership)
        orgs_membership[new_membership_id] = {
            "membership_id": new_membership_id,
            "organization_id": new_org_id,
            "user_id": user_id,
            "role": "owner",
            "status": "active",
            "joined_at": "2026-01-01T23:59:00",
        }
        return json.dumps({"success": True, "organization": orgs[new_org_id]})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_organization",
                "description": "Adds a new organization to the version control system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "organization_name": {
                            "type": "string",
                            "description": "The name of the organization to be added.",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "The authentication token of the requesting user.",
                        },
                        "description": {
                            "type": "string",
                            "description": "The description of the organization to be added.",
                        },
                    },
                    "required": ["organization_name", "auth_token"],
                },
            },
        }
