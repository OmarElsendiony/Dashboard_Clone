import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ListFilesForCommit(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        commit_id: str,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        commits = data.get("commits", {})
        file_contents = data.get("file_contents", {})
        files = data.get("files", {})

        # Validate required fields
        if not commit_id:
            return json.dumps({"success": False, "error": "commit_id must be provided"})

        if not isinstance(commit_id, str) or not commit_id.strip():
            return json.dumps({"success": False, "error": "commit_id must be a non-empty string"})

        # Normalize input
        commit_id = commit_id.strip()

        # Validate commit exists
        found_commit = None
        for _, commit in commits.items():
            if str(commit.get("commit_id")) == commit_id:
                found_commit = commit
                break

        if not found_commit:
            return json.dumps({
                "success": False,
                "error": f"Commit with ID '{commit_id}' not found"
            })

        # Find all file_contents associated with this commit
        file_ids_for_commit = set()
        for _, file_content in file_contents.items():
            if str(file_content.get("commit_id")) == commit_id:
                file_id = file_content.get("file_id")
                if file_id:
                    file_ids_for_commit.add(str(file_id))

        # Get file records for all file_ids
        files_list = []
        for file_id in file_ids_for_commit:
            # Find the file record
            for f_id, file_record in files.items():
                if str(file_record.get("file_id")) == file_id:
                    file_data = {
                        "file_id": file_record.get("file_id"),
                        "repository_id": file_record.get("repository_id"),
                        "branch_id": file_record.get("branch_id"),
                        "directory_id": file_record.get("directory_id"),
                        "file_path": file_record.get("file_path"),
                        "file_name": file_record.get("file_name"),
                        "language": file_record.get("language"),
                        "is_binary": file_record.get("is_binary", False),
                        "last_modified_at": file_record.get("last_modified_at"),
                        "last_commit_id": file_record.get("last_commit_id"),
                        "created_at": file_record.get("created_at"),
                        "updated_at": file_record.get("updated_at"),
                    }
                    files_list.append(file_data)
                    break

        # Sort files by file_path for consistent ordering
        files_list.sort(key=lambda x: x.get("file_path", ""))

        return json.dumps({
            "success": True,
            "commit_id": commit_id,
            "files_count": len(files_list),
            "files": files_list
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_files_for_commit",
                "description": "Lists all files associated with a specific commit in the version control system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "commit_id": {
                            "type": "string",
                            "description": "The ID of the commit to list files for.",
                        },
                    },
                    "required": ["commit_id"],
                },
            },
        }
