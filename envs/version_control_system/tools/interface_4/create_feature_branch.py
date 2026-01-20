import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateFeatureBranch(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        branch_name: str,
        repository_id: str,
        auth_token: str,
        base_branch_id: Optional[str] = None,
        is_default: bool = False,
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
        token_info = (
            next(
                t
                for t in access_tokens.values()
                if t.get("token_encoded") == encoded_token
            ),
            None,
        )

        token_info = token_info[0] if isinstance(token_info, tuple) else token_info

        if not token_info:
            return json.dumps(
                {"success": False, "error": "Invalid authentication token"}
            )

        requester_id = token_info["user_id"]

        # --- Validate repository ---
        repository = repositories.get(repository_id)
        if not repository:
            return json.dumps({"success": False, "error": "Repository not found"})

        # --- Authorization: write or admin ---
        has_permission = any(
            c
            for c in repository_collaborators.values()
            if c["repository_id"] == repository_id
            and c["user_id"] == requester_id
            and c["permission_level"] in {"write", "admin"}
        )

        if not has_permission:
            return json.dumps(
                {
                    "success": False,
                    "error": "Access denied. Write or admin permission required.",
                }
            )

        # --- Ensure branch name uniqueness ---
        if any(
            b
            for b in branches.values()
            if b["repository_id"] == repository_id and b["branch_name"] == branch_name
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Branch '{branch_name}' already exists in this repository",
                }
            )

        # --- Validate base branch ---
        base_branch = branches.get(base_branch_id)

        if not base_branch or base_branch["repository_id"] != repository_id:
            return json.dumps(
                {
                    "success": False,
                    "error": "Base branch does not exist in this repository",
                }
            )

        base_commit_sha = base_branch.get("commit_sha")

        # --- Generate branch ID ---
        try:
            new_branch_id = str(max(int(k) for k in branches.keys()) + 1)
        except ValueError:
            new_branch_id = "1"

        now = "2026-01-01T23:59:00"

        def generate_deterministic_sha(seed: str, prefix: str = "") -> str:
            return hashlib.sha1(f"{prefix}_{seed}".encode()).hexdigest()

        commit_sha = generate_deterministic_sha(repository_id, branch_name)
        # --- Handle default branch switch ---
        if is_default:
            repository["default_branch"] = branch_name
            for b in branches.values():
                if b["repository_id"] == repository_id and b.get("is_default"):
                    b["is_default"] = False
                    b["updated_at"] = now

        # --- Create feature branch ---
        branch_entry = {
            "branch_id": new_branch_id,
            "repository_id": repository_id,
            "branch_name": branch_name,
            "commit_sha": base_commit_sha if base_commit_sha else commit_sha,
            "source_branch": base_branch_id,
            "is_default": is_default,
            "created_at": now,
            "updated_at": now,
        }

        branches[new_branch_id] = branch_entry

        return json.dumps(
            {
                "success": True,
                "branch": branch_entry,
                "base_branch": {
                    "branch_id": base_branch_id,
                    "commit_sha": base_commit_sha,
                },
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_feature_branch",
                "description": (
                    "Creates a new feature branch from an existing base branch. "
                    "The new branch inherits the commit head of the specified base branch. "
                    "The requester must have write or admin permission on the repository."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "branch_name": {
                            "type": "string",
                            "description": "Name of the new feature branch.",
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Target repository ID.",
                        },
                        "base_branch_id": {
                            "type": "string",
                            "description": "Branch ID to create the new branch from.",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "Authentication token of the requesting user.",
                        },
                        "is_default": {
                            "type": "boolean",
                            "description": "Whether to mark the new branch as the default branch.",
                        },
                    },
                    "required": ["branch_name", "repository_id", "auth_token"],
                },
            },
        }
