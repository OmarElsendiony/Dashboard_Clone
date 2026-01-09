import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateRepoRelease(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        tag_name: str,
        release_name: str,
        target_branch_id: str,
        is_draft: str,
        is_prerelease: str,
        auth_token: str,
        description: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        access_tokens = data.get("access_tokens", {})
        repositories = data.get("repositories", {})
        repository_collaborators = data.get("repository_collaborators", {})
        branches = data.get("branches", {})
        releases = data.get("releases", {})

        def encode(text: str) -> str:
            return base64.b64encode(text.encode("utf-8")).decode("utf-8")

        def to_bool(value: str) -> bool:
            return str(value).lower() in {"true", "1", "yes"}

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

        # --- Validate repository ---
        repository = repositories.get(repository_id)
        if not repository:
            return json.dumps({"success": False, "error": "Repository not found"})

        # --- Authorization: write or admin ---
        permission = next(
            (
                c
                for c in repository_collaborators.values()
                if c.get("repository_id") == repository_id
                and c.get("user_id") == requester_id
                and c.get("permission_level") in {"write", "admin"}
            ),
            None,
        )

        if not permission:
            return json.dumps(
                {
                    "success": False,
                    "error": "Access denied. Write or admin permission required.",
                }
            )

        # --- Validate target branch ---
        branch = branches.get(target_branch_id)
        if not branch or branch.get("repository_id") != repository_id:
            return json.dumps(
                {"success": False, "error": "Target branch not found in repository"}
            )

        # --- Enforce unique tag name ---
        existing = next(
            (
                r
                for r in releases.values()
                if r.get("repository_id") == repository_id
                and r.get("tag_name") == tag_name
            ),
            None,
        )

        if existing:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Release with tag '{tag_name}' already exists",
                }
            )

        # --- Generate release ID ---
        try:
            release_id = str(max(int(k) for k in releases.keys()) + 1)
        except ValueError:
            release_id = "1"

        now = "2026-01-01T23:59:00"

        is_draft_bool = to_bool(is_draft)
        is_prerelease_bool = to_bool(is_prerelease)

        # --- Create release ---
        release = {
            "release_id": release_id,
            "repository_id": repository_id,
            "tag_name": tag_name,
            "release_name": release_name,
            "description": description,
            "author_id": requester_id,
            "target_type": "branch",
            "target_reference": branch.get("branch_name"),
            "is_draft": is_draft_bool,
            "is_prerelease": is_prerelease_bool,
            "published_at": None if is_draft_bool else now,
            "created_at": now,
        }

        releases[release_id] = release

        return json.dumps({"success": True, "release": release})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_repo_release",
                "description": (
                    "Creates a new release for a repository using a branch as the target. "
                    "The requesting user must have write or admin permission. "
                    "Releases can be created as drafts or published immediately, "
                    "and may be marked as pre-releases."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Repository where the release will be created.",
                        },
                        "tag_name": {
                            "type": "string",
                            "description": "Git tag name associated with the release.",
                        },
                        "release_name": {
                            "type": "string",
                            "description": "Human-readable name of the release.",
                        },
                        "target_branch_id": {
                            "type": "string",
                            "description": "Branch ID the release is created from.",
                        },
                        "is_draft": {
                            "type": "string",
                            "description": "Whether the release is a draft (true/false).",
                        },
                        "is_prerelease": {
                            "type": "string",
                            "description": "Whether the release is a pre-release (true/false).",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "Authentication token of the requesting user.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional release notes or description.",
                        },
                    },
                    "required": [
                        "repository_id",
                        "tag_name",
                        "release_name",
                        "target_branch_id",
                        "is_draft",
                        "is_prerelease",
                        "auth_token",
                    ],
                },
            },
        }
