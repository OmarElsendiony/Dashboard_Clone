import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreateFileContent(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        file_id: str,
        commit_id: str,
        content: str,
        encoding: str,
    ) -> str:

        def generate_id(table: Dict[str, Any]) -> str:

            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        files = data.get("files", {})
        commits = data.get("commits", {})
        file_contents = data.get("file_contents", {})

        # Validate required fields
        if not file_id:
            return json.dumps({"success": False, "error": "Missing required parameter: file_id"})

        if not commit_id:
            return json.dumps({"success": False, "error": "Missing required parameter: commit_id"})

        if not content:
            return json.dumps({"success": False, "error": "Missing required parameter: content"})

        if not encoding:
            return json.dumps({"success": False, "error": "Missing required parameter: encoding"})

        if not isinstance(content, str):
            return json.dumps({"success": False, "error": "content must be a string"})

        file_id = str(file_id).strip()
        commit_id = str(commit_id).strip()
        encoding = encoding.strip().lower()
        content = content.strip()

        # Validate encoding
        allowed_encodings = {"utf-8", "base64"}
        if encoding not in allowed_encodings:
            return json.dumps({
                "success": False,
                "error": f"encoding must be one of {', '.join(allowed_encodings)}"
            })

        # Validate file exists
        file = None
        for f_id, f in files.items():
            if str(f.get("file_id")) == file_id:
                file = f
                break

        if not file:
            return json.dumps({
                "success": False,
                "error": f"File with ID '{file_id}' not found"
            })

        # Validate commit exists
        commit = None
        for c_id, c in commits.items():
            if str(c.get("commit_id")) == commit_id:
                commit = c
                break

        if not commit:
            return json.dumps({
                "success": False,
                "error": f"Commit with ID '{commit_id}' not found"
            })

        # Validate that file belongs to the same repository as the commit
        file_repo_id = str(file.get("repository_id"))
        commit_repo_id = str(commit.get("repository_id"))
        if file_repo_id != commit_repo_id:
            return json.dumps({
                "success": False,
                "error": f"File '{file_id}' and commit '{commit_id}' belong to different repositories"
            })

        # Process content based on encoding
        content_str = None
        if encoding == "utf-8":
            content_str = content
        elif encoding == "base64":
            # If it's already a base64 string, use it as-is
            # Otherwise, encode the string to base64
            try:
                # Try to decode to see if it's already base64
                base64.b64decode(content)
                content_str = content
            except Exception:
                # If not valid base64, encode the string
                content_str = base64.b64encode(
                    content.encode("utf-8")).decode("utf-8")

        # Set timestamp
        timestamp = "2026-01-01T23:59:00"

        # Generate new content_id
        new_content_id = generate_id(file_contents)

        # Create new file content record
        new_file_content = {
            "content_id": new_content_id,
            "file_id": file_id,
            "commit_id": commit_id,
            "content": content_str,
            "encoding": encoding,
            "created_at": timestamp,
        }

        # Add the new file content to the file_contents dictionary
        file_contents[new_content_id] = new_file_content

        return json.dumps({
            "success": True,
            "message": f"File content created successfully for file '{file_id}' in commit '{commit_id}'",
            "file_content_data": {
                "content_id": new_content_id,
                "file_id": file_id,
                "commit_id": commit_id,
                "encoding": encoding,
                "created_at": timestamp,
            }
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_file_content",
                "description": "Creates a file content snapshot for a commit in the version control system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_id": {
                            "type": "string",
                            "description": "The ID of the file.",
                        },
                        "commit_id": {
                            "type": "string",
                            "description": "The ID of the commit this content is associated with.",
                        },
                        "content": {
                            "type": "string",
                            "description": "The file content.",
                        },
                        "encoding": {
                            "type": "string",
                            "description": "The encoding type.",
                            "enum": ["utf-8", "base64"]
                        },
                    },
                    "required": ["file_id", "commit_id", "content", "encoding"],
                },
            },
        }
