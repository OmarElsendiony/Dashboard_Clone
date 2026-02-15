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
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not repository_id:
            return json.dumps(
                {"success": False, "error": "repository_id is required"}
            )

        if not branch_name or not str(branch_name).strip():
            return json.dumps(
                {"success": False, "error": "branch_name is required and must be a non-empty string"}
            )
        branch_name = str(branch_name).strip()
        # Allow only characters that make sense for branch names: letters, digits, underscore, hyphen, slash, period
        if not re.fullmatch(r"[a-zA-Z0-9_\-/.]+", branch_name):
            return json.dumps(
                {
                    "success": False,
                    "error": "branch_name may only contain letters, digits, underscore (_), hyphen (-), forward slash (/), and period (.). No spaces or other special characters.",
                }
            )

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})

        if str(repository_id) not in repositories:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Repository with id '{repository_id}' not found",
                }
            )

        repository = repositories[str(repository_id)]

        if created_by is not None:
            users = data.get("users", {})
            if str(created_by) not in users:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User with id '{created_by}' not found",
                    }
                )
            user = users[str(created_by)]
            if user.get("status") != "active":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User with id '{created_by}' is not active. Current status: {user.get('status')}",
                    }
                )

        for branch in branches.values():
            if (
                str(branch.get("repository_id")) == str(repository_id)
                and branch.get("branch_name") == branch_name
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Branch '{branch_name}' already exists in repository '{repository_id}'",
                    }
                )

        if source_branch_name is None:
            source_branch_name = repository.get("default_branch")

        source_exists = any(
            str(b.get("repository_id")) == str(repository_id)
            and b.get("branch_name") == source_branch_name
            for b in branches.values()
        )
        if not source_exists:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Source branch '{source_branch_name}' does not exist in repository '{repository_id}'",
                }
            )

        if branches:
            max_id = max(int(k) for k in branches.keys())
            new_branch_id = str(max_id + 1)
        else:
            new_branch_id = "1"

        commit_sha = hashlib.sha1(
            f"{repository_id}-{branch_name}-{new_branch_id}".encode()
        ).hexdigest()

        static_timestamp = "2026-02-02 23:59:00"

        new_branch = {
            "branch_id": new_branch_id,
            "repository_id": repository_id,
            "branch_name": branch_name,
            "source_branch_name": source_branch_name,
            "commit_sha": commit_sha,
            "linked_ticket_id": linked_ticket_id,
            "created_by": created_by,
            "status": "active",
            "created_at": static_timestamp,
            "updated_at": static_timestamp,
        }

        branches[new_branch_id] = new_branch

        return json.dumps({"success": True, "branch": new_branch})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_new_branch",
                "description": "Creates a new branch in a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Repository identifier where branch will be created",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "Name for the new branch; non-empty, only letters, digits, underscore, hyphen, slash, period (e.g. fix/wide-883)",
                        },
                        "source_branch_name": {
                            "type": "string",
                            "description": "Source branch to create from",
                        },
                        "linked_ticket_id": {
                            "type": "string",
                            "description": "Ticket identifier this branch relates to",
                        },
                        "created_by": {
                            "type": "string",
                            "description": "User identifier who created the branch",
                        },
                    },
                    "required": ["repository_id", "branch_name"],
                },
            },
        }
