import json
import base64
import hashlib
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class DeleteFile(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        repository_id: str,
        branch_id: str,
        file_id: str,
        commit_message: Optional[str] = None
    ) -> str:
        """
        Delete a file from a repository branch.
        The author is automatically set to the authenticated user.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        def generate_commit_sha(repo_id: str, branch_id: str, index: int) -> str:
            seed = f"{repo_id}:{branch_id}:{index}"
            return hashlib.sha1(seed.encode()).hexdigest()

        def get_user_from_token(token: str, tokens_data: Dict[str, Any]) -> Optional[str]:
            """Encode token and find associated user_id"""
            try:
                encoded_token = base64.b64encode(token.encode("utf-8")).decode("utf-8")
                for token_info in tokens_data.values():
                    if token_info.get("token_encoded") == encoded_token:
                        return token_info.get("user_id")
                return None
            except Exception:
                return None

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        files = data.get("files", {})
        commits = data.get("commits", {})
        access_tokens = data.get("access_tokens", {})
        repository_collaborators = data.get("repository_collaborators", {})
        organization_members = data.get("organization_members", {})
        users = data.get("users", {})

        # Validate access token
        requesting_user_id = get_user_from_token(access_token, access_tokens)
        if not requesting_user_id:
            return json.dumps({
                "success": False,
                "error": "Invalid or expired access token"
            })

        author_id = requesting_user_id

        # Validate repository
        if repository_id not in repositories:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repository_id}' not found"
            })

        # Validate branch
        if branch_id not in branches:
            return json.dumps({
                "success": False,
                "error": f"Branch with ID '{branch_id}' not found"
            })

        branch = branches[branch_id]

        if branch.get("repository_id") != repository_id:
            return json.dumps({
                "success": False,
                "error": f"Branch with ID '{branch_id}' does not belong to repository '{repository_id}'"
            })

        # Validate file
        if file_id not in files:
            return json.dumps({
                "success": False,
                "error": f"File with ID '{file_id}' not found"
            })

        file_obj = files[file_id]

        if file_obj.get("repository_id") != repository_id:
            return json.dumps({
                "success": False,
                "error": f"File does not belong to repository '{repository_id}'"
            })

        if file_obj.get("branch_id") != branch_id:
            return json.dumps({
                "success": False,
                "error": f"File does not belong to branch '{branch_id}'"
            })

        if author_id not in users:
            return json.dumps({
                "success": False,
                "error": f"Authenticated user with ID '{author_id}' not found"
            })

        repository = repositories[repository_id]
        owner_id = repository.get("owner_id")
        owner_type = repository.get("owner_type")

        # Permission check
        has_permission = False

        if owner_type == "user" and owner_id == requesting_user_id:
            has_permission = True

        if not has_permission:
            for collab in repository_collaborators.values():
                if (
                    collab.get("repository_id") == repository_id and
                    collab.get("user_id") == requesting_user_id and
                    collab.get("permission_level") in ["write", "admin"] and
                    collab.get("status") == "active"
                ):
                    has_permission = True
                    break

        if not has_permission and owner_type == "organization":
            for membership in organization_members.values():
                if (
                    membership.get("organization_id") == owner_id and
                    membership.get("user_id") == requesting_user_id and
                    membership.get("status") == "active"
                ):
                    has_permission = True
                    break

        if not has_permission:
            return json.dumps({
                "success": False,
                "error": "Insufficient permissions. You must have write access to this repository to delete files"
            })

        # Parent commit resolution
        parent_commit_sha = branch.get("commit_sha")
        parent_commit_id = None

        if parent_commit_sha:
            for cid, commit in commits.items():
                if commit.get("commit_sha") == parent_commit_sha:
                    parent_commit_id = cid
                    break

        # Create commit
        timestamp = "2026-01-01T23:59:00"
        new_commit_id = generate_id(commits)

        new_commit_sha = generate_commit_sha(
            repository_id,
            branch_id,
            int(new_commit_id)
        )

        file_name = file_obj.get("file_name")

        new_commit = {
            "commit_id": new_commit_id,
            "repository_id": repository_id,
            "commit_sha": new_commit_sha,
            "author_id": author_id,
            "committer_id": author_id,
            "message": commit_message if commit_message else f"Delete {file_name}",
            "parent_commit_id": parent_commit_id,
            "committed_at": timestamp,
            "created_at": timestamp
        }

        commits[new_commit_id] = new_commit

        # Update branch pointer
        branch["commit_sha"] = new_commit_sha
        branch["updated_at"] = timestamp

        # Delete file
        deleted_file = files.pop(file_id)

        return json.dumps({
            "success": True,
            "file_id": file_id,
            "commit_id": new_commit_id,
            "deleted_file": deleted_file,
            "commit_data": new_commit
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "delete_file",
                "description": (
                    "Delete a file from a repository branch. Creates a commit to "
                    "record the deletion and updates the branch pointer. "
                    "The author is automatically set to the authenticated user."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "Access token for authentication (required)"
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Repository ID containing the file (required)"
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "Branch ID to delete the file from (required)"
                        },
                        "file_id": {
                            "type": "string",
                            "description": "File ID to delete (required)"
                        },
                        "commit_message": {
                            "type": "string",
                            "description": "Commit message for the deletion"
                        }
                    },
                    "required": ["access_token", "repository_id", "branch_id", "file_id"]
                }
            }
        }

