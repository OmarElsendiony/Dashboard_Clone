import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool
import base64


class UpdateOrganization(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        organization_name: str,
        auth_token: str,
        update_dict: Dict[str, Any],
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
            orgs.get(membership["organization_id"])
            for membership in orgs_membership.values()
            if user_id == membership["user_id"]
            and membership["organization_id"] in orgs
        ]
        target_org = next(
            (org for org in user_orgs if org["organization_name"] == organization_name),
            None,
        )
        if not target_org:
            return json.dumps({"Success": False, "message": "Organization not found"})

        # update organization details
        timestamp = "2026-01-01T23:59:00"
        org_allowed_fields = {
            "new_organization_name",
            "new_display_name",
            "new_organization_description",
        }
        membership_allowed_fields = {"new_owner_id"}
        updated_owner = None
        for key, value in update_dict.items():
            if key in org_allowed_fields:
                field_name = key.replace("new_", "")
                target_org[field_name] = value
                target_org["updated_at"] = timestamp
            elif key in membership_allowed_fields:
                # update organization owner in membership table
                for membership in orgs_membership.values():
                    if (
                        membership["organization_id"] == target_org["organization_id"]
                        and membership["user_id"] == user_id
                    ):
                        membership["user_id"] = value
                        membership["role"] = "owner"
                        membership["updated_at"] = timestamp
                        updated_owner = membership
            else:
                continue
        if not updated_owner:
            output = {"Success": True, "Organization": target_org}
        else:
            output = {
                "Success": True,
                "Organization": target_org,
                "Updated_Owner": updated_owner,
            }

        return json.dumps(output)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_organization",
                "description": "Updates details of an existing organization for the user. The update_dict parameter specifies the fields to be updated along with their new values. Fields that can be updated include 'new_owner_id', 'new_organization_name', 'new_display_name', and 'new_organization_description'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "organization_name": {
                            "type": "string",
                            "description": "The name of the organization to update.",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "The authentication token of the user.",
                        },
                        "update_dict": {
                            "type": "object",
                            "description": "A dictionary containing the fields to update and their new values. Including fields such as 'new_owner_id', 'new_organization_name', 'new_display_name' and 'new_organization_description'.",
                        },
                    },
                    "required": ["organization_name", "auth_token", "update_dict"],
                },
            },
        }
