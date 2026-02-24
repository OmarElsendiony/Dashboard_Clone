import json
import hashlib
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class AddNewBranch(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        branch_name: str,
        source_branch_name: Optional[str] = None,
        linked_ticket_id: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> str:
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return json.dumps({
                    "success": bool(False),
                    "error": "Wrong data format",
                })
        if not isinstance(data, dict):
            return json.dumps({
                "success": bool(False),
                "error": "Wrong data format",
            })

        repo_id_str = str(repository_id).strip() if repository_id is not None else ""
        if not repo_id_str:
            return json.dumps({
                "success": bool(False),
                "error": "repository_id is required",
            })

        if branch_name is None:
            return json.dumps({
                "success": bool(False),
                "error": "branch_name is required",
            })
        branch_name = str(branch_name).strip()
        if not branch_name:
            return json.dumps({
                "success": bool(False),
                "error": "branch_name is required",
            })
        if not re.fullmatch(r"[a-zA-Z0-9_\-/.]+", branch_name):
            return json.dumps({
                "success": bool(False),
                "error": "branch_name may only contain letters, digits, underscore (_), hyphen (-), forward slash (/), and period (.). No spaces or other special characters."
            })

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})

        if repo_id_str not in repositories:
            return json.dumps({
                "success": bool(False),
                "error": f"Repository with id '{repo_id_str}' not found",
            })

        repository = repositories[repo_id_str]

        if created_by is not None:
            users = data.get("users", {})
            created_by_str = str(created_by)
            if created_by_str not in users:
                return json.dumps({
                    "success": bool(False),
                    "error": f"User with id '{created_by_str}' not found",
                })
            user = users[created_by_str]
            if user.get("status") != "active":
                return json.dumps({
                    "success": bool(False),
                    "error": f"User with id '{created_by_str}' is not active. Current status: {user.get('status')}"
                })

        for branch in branches.values():
            if (
                str(branch.get("repository_id")) == repo_id_str
                and branch.get("branch_name") == branch_name
            ):
                return json.dumps({
                    "success": bool(False),
                    "error": f"Branch '{branch_name}' already exists in repository '{repo_id_str}'"
                })

        if source_branch_name is None:
            source_branch_name = repository.get("default_branch")
        if source_branch_name is None or not str(source_branch_name).strip():
            return json.dumps({
                "success": bool(False),
                "error": "Source branch could not be determined; repository default branch is missing or invalid."
            })
        source_branch_name = str(source_branch_name).strip()

        source_exists = any(
            str(b.get("repository_id")) == repo_id_str
            and b.get("branch_name") == source_branch_name
            for b in branches.values()
        )
        if not source_exists:
            return json.dumps({
                "success": bool(False),
                "error": f"Source branch '{source_branch_name}' does not exist in repository '{repo_id_str}'"
            })

        if branches:
            max_id = max(int(k) for k in branches.keys())
            new_branch_id = str(max_id + 1)
        else:
            new_branch_id = str("1")

        commit_sha = hashlib.sha1(
            f"{repo_id_str}-{branch_name}-{new_branch_id}".encode()
        ).hexdigest()

        static_timestamp = "2026-02-02 23:59:00"

        new_branch = {
            "branch_id": str(new_branch_id),
            "repository_id": str(repo_id_str),
            "branch_name": str(branch_name),
            "source_branch_name": str(source_branch_name),
            "commit_sha": str(commit_sha),
            "linked_ticket_id": str(linked_ticket_id) if linked_ticket_id is not None else None,
            "created_by": str(created_by) if created_by is not None else None,
            "status": str("active"),
            "created_at": str(static_timestamp),
            "updated_at": str(static_timestamp),
        }

        branches[new_branch_id] = new_branch

        return json.dumps({
            "success": bool(True),
            "branch": new_branch,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_new_branch",
                "description": "Creates a new branch in an existing repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Repository identifier where the branch will be created.",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "Name for the new branch; non-empty, only letters, digits, underscore, hyphen, slash, period (e.g. fix/wide-883).",
                        },
                        "source_branch_name": {
                            "type": "string",
                            "description": "Source branch to create from. Defaults to the repository default branch if omitted.",
                        },
                        "linked_ticket_id": {
                            "type": "string",
                            "description": "Ticket identifier this branch relates to.",
                        },
                        "created_by": {
                            "type": "string",
                            "description": "User identifier who created the branch.",
                        },
                    },
                    "required": ["repository_id", "branch_name"],
                },
            },
        }
