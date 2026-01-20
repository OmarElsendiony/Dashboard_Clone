import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool
import hashlib


class CreateNewBranch(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        branch_name: str,
        repository_id: str,
        auth_token: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        access_tokens = data.get("access_tokens", {})
        repositories = data.get("repositories", {})
        repository_collaborators = data.get("repository_collaborators", {})
        branches = data.get("branches", {})

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

        # --- Validate repository ---
        repository = repositories.get(repository_id)
        if not repository:
            return json.dumps({"success": False, "error": "Repository not found"})

        # --- Authorization: write or admin ---
        requester_permission = next(
            (
                c
                for c in repository_collaborators.values()
                if c.get("repository_id") == repository_id
                and c.get("user_id") == requester_id
                and c.get("permission_level") in {"write", "admin"}
            ),
            None,
        )

        if not requester_permission:
            return json.dumps(
                {
                    "success": False,
                    "error": "Access denied. Write or admin permission required.",
                }
            )

        # --- Ensure branch name uniqueness ---
        existing_branch = next(
            (b for b in branches.values() if b.get("repository_id") == repository_id),
            None,
        )

        if existing_branch:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Default branch already exists in this repository",
                }
            )

        # --- Generate branch ID ---
        try:
            new_branch_id = str(max(int(k) for k in branches.keys()) + 1)
        except ValueError:
            new_branch_id = "1"

        now = "2026-01-01T23:59:00"

        def generate_deterministic_sha(seed: str, prefix: str = "") -> str:
            return hashlib.sha1(f"{prefix}_{seed}".encode()).hexdigest()

        commit_sha = generate_deterministic_sha(repository_id, branch_name)
        # --- Create branch ---
        branch_entry = {
            "branch_id": new_branch_id,
            "repository_id": repository_id,
            "branch_name": branch_name,
            "source_branch": None,
            "commit_sha": commit_sha,
            "is_default": True,
            "created_at": now,
            "updated_at": now,
        }
        repository["default_branch"] = branch_name

        branches[new_branch_id] = branch_entry

        return json.dumps({"success": True, "branch": branch_entry})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_branch",
                "description": (
                    "Creates the default branch in a repository. No existing branch should be on the repository."
                    "The requesting user must have at least write-level permission "
                    "(write or admin) on the target repository. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "branch_name": {
                            "type": "string",
                            "description": "Name of the new branch to create.",
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "The repository in which the branch will be created.",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "Authentication token of the requesting user.",
                        },
                    },
                    "required": ["branch_name", "repository_id", "auth_token"],
                },
            },
        }
