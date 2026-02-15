import json
import hashlib
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class AddNewCommit(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        branch_id: str,
        commit_message: str,
        author_id: str,
        ticket_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not repository_id:
            return json.dumps(
                {"success": False, "error": "repository_id is required"}
            )

        if not branch_id:
            return json.dumps({"success": False, "error": "branch_id is required"})

        if not commit_message:
            return json.dumps(
                {"success": False, "error": "commit_message is required"}
            )

        if not author_id:
            return json.dumps({"success": False, "error": "author_id is required"})

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        users = data.get("users", {})
        commits = data.get("commits", {})
        tickets = data.get("tickets", {})

        if str(repository_id) not in repositories:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Repository with id '{repository_id}' not found",
                }
            )

        if str(branch_id) not in branches:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Branch with id '{branch_id}' not found",
                }
            )

        branch = branches[str(branch_id)]
        if str(branch.get("repository_id")) != str(repository_id):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Branch '{branch_id}' does not belong to repository '{repository_id}'",
                }
            )

        if branch.get("status") != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Commits can only be added to active branches. Branch '{branch_id}' has status: {branch.get('status')}",
                }
            )

        if str(author_id) not in users:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with id '{author_id}' not found",
                }
            )

        if ticket_id is not None:
            if str(ticket_id) not in tickets:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Ticket with id '{ticket_id}' not found",
                    }
                )

        if commits:
            max_id = max(int(k) for k in commits.keys())
            new_commit_id = str(max_id + 1)
        else:
            new_commit_id = "1"

        commit_sha = hashlib.sha1(
            f"{repository_id}-{branch_id}-{commit_message}-{new_commit_id}".encode()
        ).hexdigest()

        static_timestamp = "2026-02-02 23:59:00"

        new_commit = {
            "commit_id": new_commit_id,
            "repository_id": repository_id,
            "branch_id": branch_id,
            "commit_sha": commit_sha,
            "author_id": author_id,
            "commit_message": commit_message,
            "ticket_id": ticket_id,
            "committed_at": static_timestamp,
            "created_at": static_timestamp,
        }

        commits[new_commit_id] = new_commit

        branch["commit_sha"] = commit_sha
        branch["updated_at"] = static_timestamp

        return json.dumps({"success": True, "commit": new_commit})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_new_commit",
                "description": "Creates a commit in a branch with a message and author.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Repository identifier",
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "Branch identifier where commit will be added (branch must be active)",
                        },
                        "commit_message": {
                            "type": "string",
                            "description": "Commit message describing the changes",
                        },
                        "author_id": {
                            "type": "string",
                            "description": "User identifier who authored the commit",
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket identifier this commit relates to",
                        },
                    },
                    "required": [
                        "repository_id",
                        "branch_id",
                        "commit_message",
                        "author_id",
                    ],
                },
            },
        }
