import json
import os
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetRepoFile(Tool):
    """Tool for retrieving file details from a repository in the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        file_path: str,
        file_name: Optional[str] = None,
    ) -> str:
        """
        Retrieve file details by repository ID and file path.

        Args:
            data: The data dictionary containing all version control system data.
            repo_id: The ID of the repository containing the file (required).
            file_path: The full path to the file (required).
            file_name: The name of the file. If not provided, defaults to basename of file_path.

        Returns:
            JSON string containing the success status and file data if found.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        files = data.get("files", {})

        # Validate required fields
        if not repo_id or not str(repo_id).strip():
            return json.dumps({"success": False, "error": "repo_id must be provided"})

        if not file_path:
            return json.dumps({"success": False, "error": "file_path must be provided"})

        if not isinstance(file_path, str) or not file_path.strip():
            return json.dumps({"success": False, "error": "file_path must be a non-empty string"})

        # Normalize inputs
        repo_id = str(repo_id).strip()
        file_path = file_path.strip()

        # Determine file_name from file_path if not provided
        if file_name is None or not file_name.strip():
            file_name = os.path.basename(file_path)
        else:
            file_name = file_name.strip()

        # Validate repository exists
        repo = None
        for _, r in repositories.items():
            if str(r.get("repository_id")) == repo_id:
                repo = r
                break

        if not repo:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repo_id}' not found"
            })

        # Get default branch name
        default_branch_name = repo.get("default_branch", "main")

        # Find the default branch
        default_branch_id = None
        for _, branch in branches.items():
            if (
                str(branch.get("repository_id")) == repo_id
                and branch.get("branch_name") == default_branch_name
            ):
                default_branch_id = str(branch.get("branch_id"))
                break

        if not default_branch_id:
            return json.dumps({
                "success": False,
                "error": f"Default branch '{default_branch_name}' not found in repository '{repo_id}'"
            })

        # Search for file exclusively in the default branch
        found_file = None
        for _, file_record in files.items():
            if (
                str(file_record.get("repository_id")) == repo_id
                and str(file_record.get("branch_id")) == default_branch_id
                and file_record.get("file_path", "").strip() == file_path
            ):
                # Optionally check file_name if provided
                if file_name and file_record.get("file_name", "").strip() != file_name:
                    continue
                found_file = file_record.copy()
                break

        if not found_file:
            return json.dumps({
                "success": False,
                "error": f"File with path '{file_path}' not found in default branch '{default_branch_name}' of repository '{repo_id}'"
            })

        # Build the response with file data
        file_data = {
            "file_id": found_file.get("file_id"),
            "repository_id": found_file.get("repository_id"),
            "branch_id": found_file.get("branch_id"),
            "directory_id": found_file.get("directory_id"),
            "file_path": found_file.get("file_path"),
            "file_name": found_file.get("file_name"),
            "language": found_file.get("language"),
            "is_binary": found_file.get("is_binary", False),
            "last_modified_at": found_file.get("last_modified_at"),
            "last_commit_id": found_file.get("last_commit_id"),
            "created_at": found_file.get("created_at"),
            "updated_at": found_file.get("updated_at"),
        }

        return json.dumps({
            "success": True,
            "file_data": file_data
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the get_repo_file function."""
        return {
            "type": "function",
            "function": {
                "name": "get_repo_file",
                "description": "Retrieves file information from a repository's default branch by repository ID and file path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository containing the file.",
                        },
                        "file_path": {
                            "type": "string",
                            "description": "The full path to the file (e.g., '.aws/pipeline.yml', 'src/main.py').",
                        },
                        "file_name": {
                            "type": "string",
                            "description": "The name of the file. Optional.",
                        },
                    },
                    "required": ["repo_id", "file_path"],
                },
            },
        }
