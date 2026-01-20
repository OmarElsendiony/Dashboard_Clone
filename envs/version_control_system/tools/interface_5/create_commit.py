import json
import hashlib
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreateCommit(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        branch_id: str,
        actor_id: str,
        message: str,
    ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        def generate_commit_sha(repo_id: str, branch_id: str, actor_id: str, message: str, timestamp: str) -> str:
            content = f"{repo_id}:{branch_id}:{actor_id}:{message}:{timestamp}"
            return hashlib.sha1(content.encode()).hexdigest()

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        commits = data.get("commits", {})
        users = data.get("users", {})

        # Validate required fields
        if not repo_id:
            return json.dumps({"success": False, "error": "Missing required parameter: repo_id"})

        if not branch_id:
            return json.dumps({"success": False, "error": "Missing required parameter: branch_id"})

        if not actor_id:
            return json.dumps({"success": False, "error": "Missing required parameter: actor_id"})

        if not message:
            return json.dumps({"success": False, "error": "Missing required parameter: message"})

        if not isinstance(message, str) or not message.strip():
            return json.dumps({"success": False, "error": "message must be a non-empty string"})

        repo_id = str(repo_id).strip()
        branch_id = str(branch_id).strip()
        actor_id = str(actor_id).strip()
        message = message.strip()

        # Validate repository exists
        repo = None
        for r_id, r in repositories.items():
            if str(r.get("repository_id")) == repo_id:
                repo = r
                break

        if not repo:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repo_id}' not found"
            })

        # Check if repository is archived
        if repo.get("is_archived"):
            return json.dumps({
                "success": False,
                "error": f"Cannot create commit in archived repository '{repo.get('repository_name')}'"
            })

        # Validate branch exists and belongs to repository
        branch = None
        for b_id, b in branches.items():
            if str(b.get("branch_id")) == branch_id:
                if str(b.get("repository_id")) == repo_id:
                    branch = b
                    break
                else:
                    return json.dumps({
                        "success": False,
                        "error": f"Branch '{branch_id}' does not belong to repository '{repo_id}'"
                    })

        if not branch:
            return json.dumps({
                "success": False,
                "error": f"Branch with ID '{branch_id}' not found in repository '{repo_id}'"
            })

        # Validate author exists and is active
        author = None
        for u_id, u in users.items():
            if str(u.get("user_id")) == actor_id:
                author = u
                break

        if not author:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{actor_id}' not found"
            })

        if author.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"User '{actor_id}' is not active"
            })

        # Set timestamp for created_at and committed_at
        timestamp = "2026-01-01T23:59:00"

        # Get the current HEAD commit SHA from the branch
        current_commit_sha = branch.get("commit_sha")

        # Find the parent commit_id from the current HEAD commit SHA (if exists)
        parent_commit_id = None
        if current_commit_sha:
            for commit_id, commit in commits.items():
                if commit.get("commit_sha") == current_commit_sha:
                    parent_commit_id = commit.get("commit_id")
                    break

        # Generate new commit ID
        new_commit_id = generate_id(commits)

        # Generate new commit SHA
        commit_sha = generate_commit_sha(
            repo_id, branch_id, actor_id, message, timestamp)

        # Create new commit record
        new_commit = {
            "commit_id": new_commit_id,
            "repository_id": repo_id,
            "commit_sha": commit_sha,
            "author_id": actor_id,
            "committer_id": actor_id,
            "message": message,
            "parent_commit_id": parent_commit_id,
            "committed_at": timestamp,
            "created_at": timestamp,
        }

        # Add the new commit to the commits dictionary
        commits[new_commit_id] = new_commit

        return json.dumps({
            "success": True,
            "message": f"Commit created successfully in repository '{repo.get('repository_name')}' on branch '{branch.get('branch_name')}'",
            "commit_data": {
                "commit_id": new_commit_id,
                "commit_sha": commit_sha,
                "repository_id": repo_id,
                "author_id": actor_id,
                "committer_id": actor_id,
                "message": message,
                "parent_commit_id": parent_commit_id,
                "committed_at": timestamp,
                "created_at": timestamp,
            }
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_commit",
                "description":  "Creates a new commit in a repository branch in the version control system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository to create the commit in.",
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "The ID of the branch to create the commit on.",
                        },
                        "actor_id": {
                            "type": "string",
                            "description": "The ID of the user creating the commit.",
                        },
                        "message": {
                            "type": "string",
                            "description": "The commit message describing the changes.",
                        },
                    },
                    "required": ["repo_id", "branch_id", "actor_id", "message"],
                },
            },
        }
