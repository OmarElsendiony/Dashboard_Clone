import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ModifyRepository(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        auth_token: str,
        config: Dict[str, Any],
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not isinstance(config, dict):
            return json.dumps({"success": False, "error": "Invalid config format"})

        access_tokens = data.get("access_tokens", {})
        repositories = data.get("repositories", {})
        repository_collaborators = data.get("repository_collaborators", {})

        def encode(text: str) -> str:
            return base64.b64encode(text.encode("utf-8")).decode("utf-8")

        # --- Authenticate requester ---
        encoded_token = encode(auth_token)
        token_info = next(
            (
                t
                for t in access_tokens.values()
                if t.get("token_encoded") == encoded_token
            ),
            None,
        )

        if not token_info:
            return json.dumps(
                {"success": False, "error": "Invalid authentication token"}
            )

        requester_id = token_info.get("user_id")

        # --- Validate repository ---
        repository = repositories.get(repository_id)
        if not repository:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Repository with id {repository_id} not found",
                }
            )

        # --- Authorization: repository admin ---
        is_admin = any(
            m
            for m in repository_collaborators.values()
            if m.get("repository_id") == repository_id
            and m.get("user_id") == requester_id
            and m.get("permission_level") == "admin"
        )

        if not is_admin:
            return json.dumps(
                {
                    "success": False,
                    "error": "Access denied. Repository admin permission required",
                }
            )

        # --- Enum definitions ---
        VISIBILITY_ENUM = {"public", "private", "internal"}
        LICENSE_ENUM = {
            "MIT",
            "Apache-2.0",
            "GPL-3.0",
            "BSD-3-Clause",
            "unlicensed",
            "other",
        }

        # --- Allowed fields ---
        allowed_fields = {
            "description",
            "visibility",
            "is_archived",
            "is_template",
            "license_type",
        }

        updates_applied = {}
        now = "2026-01-01T23:59:00"

        # --- Validate fields & enums ---
        for key, value in config.items():
            if key not in allowed_fields:
                return json.dumps(
                    {"success": False, "error": f"Field '{key}' cannot be updated"}
                )

            if key == "visibility":
                if not isinstance(value, str) or value not in VISIBILITY_ENUM:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid visibility. Allowed values: {sorted(VISIBILITY_ENUM)}",
                        }
                    )

            elif key == "license_type":
                if not isinstance(value, str) or value not in LICENSE_ENUM:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid license_type. Allowed values: {sorted(LICENSE_ENUM)}",
                        }
                    )

            elif key in {"is_archived", "is_template"}:
                if not isinstance(value, bool):
                    return json.dumps(
                        {"success": False, "error": f"Field '{key}' must be a boolean"}
                    )

            elif key == "description":
                if value is not None and not isinstance(value, str):
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Description must be a string or null",
                        }
                    )

            updates_applied[key] = value

        # --- Apply updates ---
        for key, value in updates_applied.items():
            repository[key] = value

        repository["updated_at"] = now
        if not updates_applied:
            return json.dumps({"success": False, "message": "No update config. "})
        return json.dumps(
            {
                "success": True,
                "repository": repository,
                "updated_fields": list(updates_applied.keys()),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_repository",
                "description": (
                    "Updates configurable fields of an existing repository. "
                    "The requesting user must have admin permissions on the repository. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository to be updated.",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "Authentication token of the requesting user.",
                        },
                        "config": {
                            "type": "object",
                            "description": (
                                "A dictionary of fields to update on the repository. "
                                "Supported fields: 'description' (string|null), "
                                "'visibility' (enum: ['public', 'private', 'internal']), "
                                "'is_archived' (boolean), 'is_template' (boolean), "
                                "'license_type' (enum: ['MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause', 'unlicensed', 'other'])."
                            ),
                        },
                    },
                    "required": ["repository_id", "auth_token", "config"],
                },
            },
        }
