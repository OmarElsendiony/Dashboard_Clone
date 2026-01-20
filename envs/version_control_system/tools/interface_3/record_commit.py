import hashlib
import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class RecordCommit(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        branch_id: str,
        author_id: str,
        message: str,
        file_id: str,
        content: str,
        encoding: str
    ) -> str:
        def generate_deterministic_sha(seed: str, prefix: str = "") -> str:
            """Generates a pseudo-random deterministic SHA-1 hash."""
            return hashlib.sha1(f"{prefix}_{seed}".encode()).hexdigest()

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required to record commit"})
        if not branch_id:
            return json.dumps({"success": False, "error": "branch_id is required to record commit"})
        if not author_id:
            return json.dumps({"success": False, "error": "author_id is required to record commit"})
        if not message:
            return json.dumps({"success": False, "error": "message is required to record commit"})
        if not file_id:
            return json.dumps({"success": False, "error": "file_id is required to record commit"})
        if not content:
            return json.dumps({"success": False, "error": "content is required to record commit"})
        if not encoding:
            return json.dumps({"success": False, "error": "encoding is required to record commit"})

        # Validate encoding
        valid_encodings = ["utf-8", "base64", "binary"]
        if encoding not in valid_encodings:
            return json.dumps({"success": False, "error": f"Invalid encoding '{encoding}'. Valid values: {', '.join(valid_encodings)}"})

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        users = data.get("users", {})
        commits = data.get("commits", {})
        files = data.get("files", {})
        file_contents = data.get("file_contents", {})

        # Validate repository exists
        if str(repository_id) not in repositories:
            return json.dumps({"success": False, "error": f"Repository with id '{repository_id}' not found"})

        # Validate branch exists
        if str(branch_id) not in branches:
            return json.dumps({"success": False, "error": f"Branch with id '{branch_id}' not found"})

        # Validate branch belongs to the repository
        branch = branches[str(branch_id)]
        if str(branch.get("repository_id")) != str(repository_id):
            return json.dumps({"success": False, "error": f"Branch '{branch_id}' does not belong to repository '{repository_id}'"})

        # Validate author exists
        if str(author_id) not in users:
            return json.dumps({"success": False, "error": f"User with id '{author_id}' not found"})

        # Validate file exists
        if str(file_id) not in files:
            return json.dumps({"success": False, "error": f"File with id '{file_id}' not found"})

        # Generate new commit_id
        if commits:
            max_commit_id = max(int(k) for k in commits.keys())
            new_commit_id = str(max_commit_id + 1)
        else:
            new_commit_id = "1"

        # Generate deterministic commit SHA
        seed = f"{repository_id}_{branch_id}_{author_id}_{message}_{new_commit_id}"
        commit_sha = generate_deterministic_sha(seed, "commit")

        # Create commit record
        new_commit = {
            "commit_id": new_commit_id,
            "repository_id": repository_id,
            "branch_id": branch_id,
            "commit_sha": commit_sha,
            "author_id": author_id,
            "message": message,
            "committed_at": "2026-01-01T23:59:00",
            "created_at": "2026-01-01T23:59:00"
        }

        commits[new_commit_id] = new_commit

        # Generate new content_id
        if file_contents:
            max_content_id = max(int(k) for k in file_contents.keys())
            new_content_id = str(max_content_id + 1)
        else:
            new_content_id = "1"

        # Create file content record
        new_file_content = {
            "content_id": new_content_id,
            "file_id": file_id,
            "commit_id": new_commit_id,
            "content": content,
            "encoding": encoding,
            "created_at": "2026-01-01T23:59:00"
        }

        file_contents[new_content_id] = new_file_content

        return json.dumps({"success": True, "result": {"commit": new_commit, "file_content": new_file_content}})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "record_commit",
                "description": "Records a new commit in a repository branch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository."
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "The unique identifier of the branch the commit belongs to."
                        },
                        "author_id": {
                            "type": "string",
                            "description": "The unique identifier of the user who authored the commit."
                        },
                        "message": {
                            "type": "string",
                            "description": "The commit message describing the changes."
                        },
                        "file_id": {
                            "type": "string",
                            "description": "The unique identifier of the file being committed."
                        },
                        "content": {
                            "type": "string",
                            "description": "The content of the file being committed."
                        },
                        "encoding": {
                            "type": "string",
                            "description": "The encoding of the file content. Valid values: utf-8, base64, binary."
                        }
                    },
                    "required": ["repository_id", "branch_id", "author_id", "message", "file_id", "content", "encoding"]
                }
            }
        }
