import json
import hashlib
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateCommit(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_name: str,
        branch_name: str,
        commit_message: str,
        commit_type: str,
        author_email: str,
        ticket_id: Optional[str] = None,
    ) -> str:
        if not repository_name:
            return json.dumps({"error": "repository_name is required"})

        if not branch_name:
            return json.dumps({"error": "branch_name is required"})

        if not commit_message:
            return json.dumps({"error": "commit_message is required"})

        if not commit_type:
            return json.dumps({"error": "commit_type is required"})

        if not author_email:
            return json.dumps({"error": "author_email is required"})

        valid_commit_types = ("fix", "feat", "chore")
        if commit_type not in valid_commit_types:
            return json.dumps(
                {"error": f"Invalid commit_type '{commit_type}'. Must be one of: {', '.join(valid_commit_types)}"}
            )

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        users = data.get("users", {})
        commits = data.get("commits", {})
        timestamp = "2026-02-02 23:59:00"

        repository_id = None
        for r_id, repo in repositories.items():
            if repo.get("repository_name") == str(repository_name):
                repository_id = r_id
                break

        if not repository_id:
            return json.dumps({"error": f"Repository with name '{repository_name}' not found"})

        branch_details = None
        for branch in branches.values():
            if (
                branch.get("branch_name") == str(branch_name) and
                str(branch.get("repository_id")) == str(repository_id)
            ):
                branch_details = branch
                break

        if not branch_details:
            return json.dumps(
                {"error": f"Branch '{branch_name}' not found in repository '{repository_name}'"}
            )

        branch_id = str(branch_details["branch_id"])

        author_id = None
        for u_id, user in users.items():
            if user.get("email") == str(author_email) and user.get("status") == "active":
                author_id = u_id
                break

        if not author_id:
            return json.dumps({"error": f"Active user with email '{author_email}' not found"})

        if ticket_id:
            linked_ticket_id = branch_details.get("linked_ticket_id")
            if linked_ticket_id and str(linked_ticket_id) != str(ticket_id):
                return json.dumps(
                    {"error": f"Mismatch: ticket_id '{ticket_id}' does not match branch linked_ticket_id '{linked_ticket_id}'"}
                )

        if not commits:
            commit_id = "1"
        else:
            commit_id = str(max(int(k) for k in commits.keys()) + 1)

        def generate_commit_sha(seed):
            return hashlib.sha1(f"commit_{seed}".encode()).hexdigest()

        seed = f"{repository_id}_{branch_id}_{author_id}_{commit_message}_{commit_id}"
        commit_sha = generate_commit_sha(seed)

        new_commit = {
            "commit_id": str(commit_id),
            "repository_id": str(repository_id),
            "branch_id": str(branch_id),
            "commit_sha": str(commit_sha),
            "author_id": str(author_id),
            "commit_message": str(commit_message),
            "commit_type": str(commit_type),
            "ticket_id": str(ticket_id) if ticket_id else None,
            "committed_at": timestamp,
            "created_at": timestamp,
        }

        commits[commit_id] = new_commit

        branch_details["commit_sha"] = str(commit_sha)
        branch_details["updated_at"] = timestamp

        return json.dumps({
            "success": True,
            "commit": {
                "commit_id": str(new_commit["commit_id"]),
                "repository_id": str(new_commit["repository_id"]),
                "branch_id": str(new_commit["branch_id"]),
                "commit_sha": str(new_commit["commit_sha"]),
                "author_id": str(new_commit["author_id"]),
                "commit_message": str(new_commit["commit_message"]),
                "commit_type": str(new_commit["commit_type"]),
                "ticket_id": new_commit["ticket_id"],
                "committed_at": str(new_commit["committed_at"]),
                "created_at": str(new_commit["created_at"]),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_commit",
                "description": "Creates a new commit on a specified branch of a repository. It should be used when you need to commit changes to a branch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_name": {
                            "type": "string",
                            "description": "The name of the repository",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "The name of the branch",
                        },
                        "commit_message": {
                            "type": "string",
                            "description": "The commit message",
                        },
                        "commit_type": {
                            "type": "string",
                            "description": "The type of the commit",
                            "enum": ["fix", "feat", "chore"],
                        },
                        "author_email": {
                            "type": "string",
                            "description": "The email of the commit author",
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "The ticket ID to associate with the commit",
                        },
                    },
                    "required": ["repository_name", "branch_name", "commit_message", "commit_type", "author_email"],
                },
            },
        }
