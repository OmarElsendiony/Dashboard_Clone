import json
import os
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateOrUpdateFile(Tool):
    """Tool for creating or updating a file record in a repository branch in the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        branch_id: str,
        commit_id: str,
        file_path: str,
        language: str,
        file_name: Optional[str] = None,
    ) -> str:
        """
        Create or update a file record in a repository branch.

        Args:
            data: The data dictionary containing all version control system data.
            repo_id: The ID of the repository (required).
            branch_id: The ID of the branch (required).
            commit_id: The ID of the commit this file is associated with (required).
            file_path: The full path to the file (required).
            file_name: The name of the file. If not provided, defaults to basename of file_path.
            language: The programming language of the file (required).

        Returns:
            str: A JSON-encoded string containing the success status and file data.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            """
            Generates a new unique ID for a record.

            Returns:
                str: The new unique ID as a string.
            """
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        commits = data.get("commits", {})
        files = data.get("files", {})
        directories = data.get("directories", {})

        # Validate required fields
        if not repo_id:
            return json.dumps({"success": False, "error": "Missing required parameter: repo_id"})

        if not branch_id:
            return json.dumps({"success": False, "error": "Missing required parameter: branch_id"})

        if not commit_id:
            return json.dumps({"success": False, "error": "Missing required parameter: commit_id"})

        if not file_path:
            return json.dumps({"success": False, "error": "Missing required parameter: file_path"})

        repo_id = str(repo_id).strip()
        branch_id = str(branch_id).strip()
        commit_id = str(commit_id).strip()
        file_path = file_path.strip()
        
        if not language or (isinstance(language, str) and not language.strip()):
            return json.dumps({"success": False, "error": "Missing required parameter: language"})
        
        language = language.strip() if isinstance(language, str) else str(language).strip()

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

        # Validate commit exists
        commit = None
        for c_id, c in commits.items():
            if str(c.get("commit_id")) == commit_id:
                if str(c.get("repository_id")) == repo_id:
                    commit = c
                    break
                else:
                    return json.dumps({
                        "success": False,
                        "error": f"Commit '{commit_id}' does not belong to repository '{repo_id}'"
                    })

        if not commit:
            return json.dumps({
                "success": False,
                "error": f"Commit with ID '{commit_id}' not found in repository '{repo_id}'"
            })

        # Determine file_name from file_path if not provided
        if file_name is None or not file_name.strip():
            file_name = os.path.basename(file_path)
        else:
            file_name = file_name.strip()

        # Find or determine directory_id from file_path
        directory_id = None
        if file_path and file_path != file_name:
            # Extract directory path (parent directory)
            dir_path = os.path.dirname(file_path)
            if dir_path:
                # Look for existing directory with matching path, repo_id, and branch_id
                for d_id, d in directories.items():
                    if (
                        str(d.get("repository_id")) == repo_id
                        and str(d.get("branch_id")) == branch_id
                        and d.get("directory_path", "").strip() == dir_path
                    ):
                        directory_id = d.get("directory_id")
                        break

        # Set timestamp
        timestamp = "2026-01-01T23:59:00"

        # Check if file already exists for this repo, branch, and path
        existing_file = None
        existing_file_id = None
        for f_id, f in files.items():
            if (
                str(f.get("repository_id")) == repo_id
                and str(f.get("branch_id")) == branch_id
                and f.get("file_path", "").strip() == file_path
            ):
                existing_file = f
                existing_file_id = f_id
                break

        if existing_file:
            # Update existing file
            existing_file["last_commit_id"] = commit_id
            existing_file["last_modified_at"] = timestamp
            existing_file["updated_at"] = timestamp
            # Update language if provided
            if language:
                existing_file["language"] = language
            # Update file_name if it changed
            if file_name:
                existing_file["file_name"] = file_name
            # Update directory_id if found
            if directory_id:
                existing_file["directory_id"] = directory_id

            return json.dumps({
                "success": True,
                "message": f"File '{file_path}' updated successfully",
                "file_data": {
                    "file_id": existing_file.get("file_id"),
                    "repository_id": existing_file.get("repository_id"),
                    "branch_id": existing_file.get("branch_id"),
                    "directory_id": existing_file.get("directory_id"),
                    "file_path": existing_file.get("file_path"),
                    "file_name": existing_file.get("file_name"),
                    "language": existing_file.get("language"),
                    "is_binary": existing_file.get("is_binary", False),
                    "last_modified_at": existing_file.get("last_modified_at"),
                    "last_commit_id": existing_file.get("last_commit_id"),
                    "created_at": existing_file.get("created_at"),
                    "updated_at": existing_file.get("updated_at"),
                }
            })
        else:
            # Create new file record
            new_file_id = generate_id(files)

            new_file = {
                "file_id": new_file_id,
                "repository_id": repo_id,
                "branch_id": branch_id,
                "directory_id": directory_id,
                "file_path": file_path,
                "file_name": file_name,
                "language": language,
                "is_binary": False,
                "last_modified_at": timestamp,
                "last_commit_id": commit_id,
                "created_at": timestamp,
                "updated_at": timestamp,
            }

            # Add the new file to the files dictionary
            files[new_file_id] = new_file

            return json.dumps({
                "success": True,
                "message": f"File '{file_path}' created successfully",
                "file_data": {
                    "file_id": new_file_id,
                    "repository_id": repo_id,
                    "branch_id": branch_id,
                    "directory_id": directory_id,
                    "file_path": file_path,
                    "file_name": file_name,
                    "language": language,
                    "is_binary": False,
                    "last_modified_at": timestamp,
                    "last_commit_id": commit_id,
                    "created_at": timestamp,
                    "updated_at": timestamp,
                }
            })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the create_or_update_file function."""
        return {
            "type": "function",
            "function": {
                "name": "create_or_update_file",
                "description": "Creates or updates a file record in a repository branch in the version control system. This function ensures a file record exists for the specified repository, branch, and file path. If a file with the same repository_id, branch_id, and file_path already exists, it updates the file record (updates last_commit_id, last_modified_at, and optionally language and file_name). If the file doesn't exist, it creates a new file record. The file_name parameter is optional and defaults to the basename of file_path if not provided. The directory_id is automatically determined from the file_path if a matching directory exists. Use this after confirming the repository exists using get_repo, the branch exists using get_repo_branch, and the commit exists using create_commit. After creating or updating the file record, you typically need to save the file content using create_file_content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository. Required field. The repository must exist.",
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "The ID of the branch. Required field. The branch must exist and belong to the specified repository.",
                        },
                        "commit_id": {
                            "type": "string",
                            "description": "The ID of the commit this file is associated with. Required field. The commit must exist and belong to the specified repository.",
                        },
                        "file_path": {
                            "type": "string",
                            "description": "The full path to the file (e.g., 'src/main.py', '.github/workflows/ci.yml'). Required field.",
                        },
                        "file_name": {
                            "type": "string",
                            "description": "The name of the file. Optional - if not provided, defaults to the basename of file_path (e.g., 'main.py' from 'src/main.py').",
                        },
                        "language": {
                            "type": "string",
                            "description": "The programming language of the file (e.g., 'Python', 'JavaScript', 'YAML', 'Go'). Required field.",
                        },
                    },
                    "required": ["repo_id", "branch_id", "commit_id", "file_path", "language"],
                },
            },
        }
