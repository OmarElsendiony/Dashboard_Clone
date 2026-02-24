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
        if isinstance(data, str):
            data = json.loads(data)
        if not isinstance(data, dict):
            return json.dumps({"success": bool(False), "error": str("Invalid data format")})
        if repository_id is None or repository_id == "":
            return json.dumps(
                {"success": bool(False), "error": str("repository_id is required")}
            )
        if branch_id is None or branch_id == "":
            return json.dumps({"success": bool(False), "error": str("branch_id is required")})
        if commit_message is None or commit_message == "":
            return json.dumps(
                {"success": bool(False), "error": str("commit_message is required")}
            )
        if author_id is None or author_id == "":
            return json.dumps({"success": bool(False), "error": str("author_id is required")})

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        users = data.get("users", {})
        commits = data.get("commits")
        if commits is None:
            commits = {}
            data["commits"] = commits
        tickets = data.get("tickets", {})

        if str(repository_id) not in repositories:
            return json.dumps(
                {
                    "success": bool(False),
                    "error": str(f"Repository with id \"{repository_id}\" not found"),
                }
            )
        if str(branch_id) not in branches:
            return json.dumps(
                {
                    "success": bool(False),
                    "error": str(f"Branch with id \"{branch_id}\" not found"),
                }
            )
        branch = branches[str(branch_id)]
        if str(branch.get("repository_id")) != str(repository_id):
            return json.dumps(
                {
                    "success": bool(False),
                    "error": str(f"Branch \"{branch_id}\" does not belong to repository \"{repository_id}\""),
                }
            )
        if branch.get("status") != "active":
            return json.dumps(
                {
                    "success": bool(False),
                    "error": str(f"Commits can only be added to active branches. Branch \"{branch_id}\" has status: {branch.get('status')}"),
                }
            )
        if str(author_id) not in users:
            return json.dumps(
                {
                    "success": bool(False),
                    "error": str(f"User with id \"{author_id}\" not found"),
                }
            )
        if ticket_id is not None and ticket_id != "":
            if str(ticket_id) not in tickets:
                return json.dumps(
                    {
                        "success": bool(False),
                        "error": str(f"Ticket with id \"{ticket_id}\" not found"),
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
            "repository_id": str(repository_id),
            "branch_id": str(branch_id),
            "commit_sha": commit_sha,
            "author_id": str(author_id),
            "commit_message": str(commit_message),
            "ticket_id": str(ticket_id) if ticket_id else None,
            "committed_at": str(static_timestamp),
            "created_at": str(static_timestamp),
        }
        commits[new_commit_id] = new_commit
        branch["commit_sha"] = commit_sha
        branch["updated_at"] = static_timestamp

        out_commit = {
            "commit_id": str(new_commit["commit_id"]),
            "repository_id": str(new_commit["repository_id"]),
            "branch_id": str(new_commit["branch_id"]),
            "commit_sha": str(new_commit["commit_sha"]),
            "author_id": str(new_commit["author_id"]),
            "commit_message": str(new_commit["commit_message"]),
            "ticket_id": str(new_commit["ticket_id"]) if new_commit["ticket_id"] is not None else None,
            "committed_at": str(new_commit["committed_at"]),
            "created_at": str(new_commit["created_at"]),
        }
        return json.dumps({"success": bool(True), "commit": out_commit})

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
                            "description": "Repository identifier.",
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "Branch identifier where the commit will be added (branch must be active).",
                        },
                        "commit_message": {
                            "type": "string",
                            "description": "Commit message describing the changes.",
                        },
                        "author_id": {
                            "type": "string",
                            "description": "User identifier who authored the commit.",
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket identifier this commit relates to, if any.",
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
