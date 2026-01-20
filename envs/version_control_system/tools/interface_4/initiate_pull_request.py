import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class InitiatePullRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        auth_token: str,
        source_branch_id: str,
        target_branch_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        access_tokens = data.get("access_tokens", {})
        repositories = data.get("repositories", {})
        repository_collaborators = data.get("repository_collaborators", {})
        branches = data.get("branches", {})
        pull_requests = data.get("pull_requests", {})

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

        requester_id = token_info["user_id"]

        # --- Validate branches ---
        source_branch = branches.get(source_branch_id)
        target_branch = branches.get(target_branch_id)

        if not source_branch:
            return json.dumps({"success": False, "error": "Source branch not found"})

        if not target_branch:
            return json.dumps({"success": False, "error": "Target branch not found"})

        if source_branch["repository_id"] != target_branch["repository_id"]:
            return json.dumps(
                {
                    "success": False,
                    "error": "Branches must belong to the same repository",
                }
            )

        repository_id = source_branch["repository_id"]

        if repository_id not in repositories:
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

        # --- Prevent duplicate open PR ---

        open_pr = [
            pr
            for pr in pull_requests.values()
            if pr["repository_id"] == repository_id
            and pr["source_branch"] == source_branch["branch_name"]
            and pr["target_branch"] == target_branch["branch_name"]
            and pr["status"] in {"open", "draft"}
        ]
        if open_pr:
            opr_id = open_pr[0]["pull_request_id"]
            return json.dumps(
                {
                    "success": False,
                    "message": f"An open pull request already exists for these branches. Pull request ID: {opr_id}",
                }
            )

        # --- Generate pull request ID ---
        try:
            next_pr_id = str(max(int(k) for k in pull_requests.keys()) + 1)
        except ValueError:
            next_pr_id = "1"

        # --- Pull request number ---
        repo_pr_numbers = [pr["pull_request_number"] for pr in pull_requests.values()]
        next_pr_number = int(max([int(_) for _ in repo_pr_numbers], default=0)) + 1

        now = "2026-01-01T23:59:00"
        default_title = (
            f"Merge {source_branch['branch_name']} into {target_branch['branch_name']}"
        )
        pr_entry = {
            "pull_request_id": next_pr_id,
            "repository_id": repository_id,
            "pull_request_number": int(next_pr_number),
            "title": title if title else default_title,
            "description": description,
            "author_id": requester_id,
            "source_branch": source_branch["branch_name"],
            "target_branch": target_branch["branch_name"],
            "status": "open",
            "merged_by": None,
            "merged_at": None,
            "closed_at": None,
            "created_at": now,
            "updated_at": now,
        }

        pull_requests[next_pr_id] = pr_entry

        return json.dumps({"success": True, "pull_request": pr_entry})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "initiate_pull_request",
                "description": (
                    "Creates a new pull request (PR) from a source branch to a target branch "
                    "within the same repository. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "auth_token": {
                            "type": "string",
                            "description": (
                                "Authentication token identifying the requesting user. "
                                "The token must be valid and correspond to a user with "
                                "write or admin permission on the repository."
                            ),
                        },
                        "source_branch_id": {
                            "type": "string",
                            "description": (
                                "The unique identifier of the source branch containing "
                                "the proposed changes to be merged."
                            ),
                        },
                        "target_branch_id": {
                            "type": "string",
                            "description": (
                                "The unique identifier of the target branch into which "
                                "the source branch changes will be merged."
                            ),
                        },
                        "title": {
                            "type": "string",
                            "description": (
                                "Optional human-readable title for the pull request. "
                                "If omitted, a default title is generated automatically."
                            ),
                        },
                        "description": {
                            "type": "string",
                            "description": (
                                "Optional detailed description explaining the purpose, "
                                "scope, or context of the pull request."
                            ),
                        },
                    },
                    "required": ["auth_token", "source_branch_id", "target_branch_id"],
                },
            },
        }
