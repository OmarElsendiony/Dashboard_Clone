import json
import hashlib
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class UpdateFile(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        branch_id: str,
        file_id: str,
        file_path: str,
        file_name: str,
        content: str,
        encoding: str,
        commit_message: str,
        user_id: str,
    ) -> str:
        """Update a file by creating a new commit and file_content record."""
        timestamp = "2026-01-01T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        def generate_commit_sha(commit_id: str) -> str:
            """Generate commit SHA using hashlib."""
            return hashlib.sha1(f"commit_{commit_id}".encode()).hexdigest()

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        # Get data containers
        files_dict = data.get("files", {})
        file_contents_dict = data.get("file_contents", {})
        commits_dict = data.get("commits", {})
        branches_dict = data.get("branches", {})
        repositories_dict = data.get("repositories", {})
        users_dict = data.get("users", {})

        # Convert to strings
        repository_id_str = str(repository_id).strip()
        branch_id_str = str(branch_id).strip()
        file_id_str = str(file_id).strip()
        file_path_str = str(file_path).strip()
        file_name_str = str(file_name).strip()
        content_str = str(content)
        encoding_str = str(encoding).strip()
        commit_message_str = str(commit_message).strip()
        user_id_str = str(user_id).strip()

        # Validate repository exists
        if repository_id_str not in repositories_dict:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repository_id_str}' not found",
            })

        # Validate branch exists
        if branch_id_str not in branches_dict:
            return json.dumps({
                "success": False,
                "error": f"Branch with ID '{branch_id_str}' not found",
            })

        # Validate branch belongs to repository
        branch = branches_dict[branch_id_str]
        if str(branch.get("repository_id")) != repository_id_str:
            return json.dumps({
                "success": False,
                "error": f"Branch '{branch_id_str}' does not belong to repository '{repository_id_str}'",
            })

        # Validate file exists
        if file_id_str not in files_dict:
            return json.dumps({
                "success": False,
                "error": f"File with ID '{file_id_str}' not found",
            })

        # Validate file belongs to repository
        file_record = files_dict[file_id_str]
        if str(file_record.get("repository_id")) != repository_id_str:
            return json.dumps({
                "success": False,
                "error": f"File '{file_id_str}' does not belong to repository '{repository_id_str}'",
            })

        # Validate user exists
        if user_id_str not in users_dict:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{user_id_str}' not found",
            })

        # Validate encoding
        valid_encodings = ["utf-8", "base64", "binary"]
        if encoding_str not in valid_encodings:
            return json.dumps({
                "success": False,
                "error": f"Invalid encoding '{encoding_str}'. Must be one of: {', '.join(valid_encodings)}",
            })

        # Create commit
        new_commit_id = generate_id(commits_dict)
        commit_sha = generate_commit_sha(new_commit_id)
        new_commit = {
            "commit_id": new_commit_id,
            "repository_id": repository_id_str,
            "commit_sha": commit_sha,
            "commit_message": commit_message_str,
            "author_id": user_id_str,
            "committer_id": user_id_str,
            "committed_at": timestamp,
            "created_at": timestamp,
        }
        commits_dict[new_commit_id] = new_commit

        # Create new file_content record with new content and commit_id
        new_content_id = generate_id(file_contents_dict)
        new_file_content = {
            "content_id": new_content_id,
            "file_id": file_id_str,
            "commit_id": new_commit_id,
            "content": content_str,
            "encoding": str(encoding_str),
            "created_at": timestamp,
        }
        file_contents_dict[new_content_id] = new_file_content

        # Update file record with last_commit_id and updated_at
        files_dict[file_id_str]["last_commit_id"] = new_commit_id
        files_dict[file_id_str]["updated_at"] = timestamp

        # Update branch with new commit_sha
        branches_dict[branch_id_str]["commit_sha"] = commit_sha

        return json.dumps({
            "success": True,
            "file": files_dict[file_id_str],
            "file_content": new_file_content,
            "commit": new_commit,
            "message": f"File '{file_name_str}' updated successfully with commit {commit_sha[:7]}",
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the update_file function."""
        return {
            "type": "function",
            "function": {
                "name": "update_file",
                "description": (
                    "Update a file by creating a new commit and file_content record. "
                    "Validates that repository, branch, file, and user exist. "
                    "Validates that branch and file belong to the repository. "
                    "Validates encoding is one of: utf-8, base64, binary. "
                    "Only the content is updated - creates a new file_content record with new content and commit_id. "
                    "Creates a new commit record with SHA-1 hash generated from 'commit_{commit_id}'. "
                    "Updates the file's last_commit_id field. "
                    "Updates the branch's commit_sha to the newly created commit. "
                    "Returns the updated file, new file_content, and commit details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository.",
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "The ID of the branch where the file is being updated.",
                        },
                        "file_id": {
                            "type": "string",
                            "description": "The ID of the file to update.",
                        },
                        "file_path": {
                            "type": "string",
                            "description": "The path of the file (for validation/reference).",
                        },
                        "file_name": {
                            "type": "string",
                            "description": "The name of the file (for validation/reference).",
                        },
                        "content": {
                            "type": "string",
                            "description": "The new content of the file.",
                        },
                        "encoding": {
                            "type": "string",
                            "description": "The encoding of the file. Valid values: utf-8, base64, binary.",
                        },
                        "commit_message": {
                            "type": "string",
                            "description": "The commit message for this file update.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user updating the file (used as author_id and committer_id).",
                        },
                    },
                    "required": ["repository_id", "branch_id", "file_id", "file_path", "file_name", "content", "encoding", "commit_message", "user_id"],
                },
            },
        }
