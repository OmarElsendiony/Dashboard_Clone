import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ApproveRelease(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any], release_id: str, approval_decision: str, auth_token: str
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        access_tokens = data.get("access_tokens", {})
        repositories = data.get("repositories", {})
        repository_collaborators = data.get("repository_collaborators", {})
        releases = data.get("releases", {})

        def encode(text: str) -> str:
            return base64.b64encode(text.encode("utf-8")).decode("utf-8")

        now = "2026-01-01T23:59:00"

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

        # --- Validate release ---
        release = releases.get(release_id)
        if not release:
            return json.dumps({"success": False, "error": "Release not found"})

        repository_id = release.get("repository_id")
        if repository_id not in repositories:
            return json.dumps({"success": False, "error": "Repository not found"})

        # --- Authorization ---
        permission = next(
            (
                c
                for c in repository_collaborators.values()
                if c.get("repository_id") == repository_id
                and c.get("user_id") == requester_id
                and c.get("permission_level") in {"admin", "write"}
            ),
            None,
        )

        if not permission:
            return json.dumps(
                {
                    "success": False,
                    "error": "Access denied. Admin or write permission required.",
                }
            )

        # --- Validate decision ---
        decision = approval_decision.lower()
        if decision not in {"publish", "reject", "unpublish"}:
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid approval_decision. Use 'publish', 'reject', or 'unpublish'.",
                }
            )

        # --- Enforce lifecycle rules ---
        if decision == "publish" and not release.get("is_draft"):
            return json.dumps(
                {"success": False, "error": "Only draft releases can be published."}
            )

        # --- Apply decision ---
        if decision == "publish":
            release["is_draft"] = False
            release["published_at"] = now
            action = "published"

        elif decision == "reject":
            release["is_draft"] = True
            release["published_at"] = None
            action = "rejected"

        elif decision == "unpublish":
            release["is_draft"] = True
            release["published_at"] = None
            action = "unpublished"

        release["updated_at"] = now

        return json.dumps({"success": True, "action": action, "release": release})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "approve_release",
                "description": (
                    "Finalizes a draft repository release. Only draft releases can be finalized."
                    "User must have admin/write permission on the repository"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "release_id": {
                            "type": "string",
                            "description": "The draft release to finalize.",
                        },
                        "approval_decision": {
                            "type": "string",
                            "description": "Decision to approve (publish) or reject the release.",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "Authentication token of the requesting admin.",
                        },
                    },
                    "required": ["release_id", "approval_decision", "auth_token"],
                },
            },
        }
