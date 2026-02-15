import json
from typing import Any, Dict, Optional, List
from tau_bench.envs.tool import Tool

class SearchCode(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        branch_id: str,
        file_paths: Optional[List[str]] = None,
    ) -> str:
        timestamp = "2026-02-02 23:59:00"
        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        if not repository_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'repository_id'"})

        if not branch_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'branch_id'"})

        # Validate file_paths format
        if file_paths is not None:
            if not isinstance(file_paths, list):
                return json.dumps({
                    "success": False,
                    "error": "Invalid format: 'file_paths' must be a list of strings"
                })

            # Check if empty list
            if len(file_paths) == 0:
                return json.dumps({
                    "success": False,
                    "error": "Invalid format: 'file_paths' cannot be an empty list. Either omit the parameter or provide at least one file path."
                })

            for path in file_paths:
                if not isinstance(path, str):
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid format: all file paths must be strings, found {type(path).__name__}"
                    })
                if not path.strip():
                    return json.dumps({
                        "success": False,
                        "error": "Invalid format: file paths cannot be empty strings"
                    })

        # Validate that branch belongs to the repository
        branches_dict = data.get("branches", {})
        branch_found = False
        branch_belongs_to_repo = False

        for _, b_data in branches_dict.items():
            if str(b_data.get("branch_id", "")) == branch_id:
                branch_found = True
                if str(b_data.get("repository_id", "")) == repository_id:
                    branch_belongs_to_repo = True
                break

        if not branch_found:
            return json.dumps({
                "success": False,
                "error": f"Branch '{branch_id}' does not exist"
            })

        if not branch_belongs_to_repo:
            return json.dumps({
                "success": False,
                "error": f"Branch '{branch_id}' does not belong to repository '{repository_id}'"
            })

        files_dict = data.get("files", {})

        # Convert file_paths to set for efficient lookup (strip whitespace and ensure strings)
        file_path_set = set(str(path).strip() for path in file_paths) if file_paths else None

        results = []

        for _, f_data in files_dict.items():
            # Apply repository filter (required)
            if str(f_data.get("repository_id", "")) != repository_id:
                continue

            # Apply branch filter (required)
            if str(f_data.get("branch_id", "")) != branch_id:
                continue

            # Get the file path from the data
            current_file_path = str(f_data.get("file_path", "")).strip()

            # Apply file_paths filter (optional)
            # If file_path_set is specified, ONLY include files in that set
            if file_path_set is not None and current_file_path not in file_path_set:
                continue

            # Build result object with content always included
            file_info = {
                "file_id": str(f_data.get("file_id", "")),
                "repository_id": str(f_data.get("repository_id", "")),
                "branch_id": str(f_data.get("branch_id", "")),
                "file_path": str(f_data.get("file_path", "")),
                "file_name": str(f_data.get("file_name", "")),
                "content": str(f_data.get("content", "")),
                "is_binary": str(f_data.get("is_binary", "false")),
                "last_commit_id": str(f_data.get("last_commit_id", "")),
                "created_at": str(f_data.get("created_at", timestamp)),
                "updated_at": str(f_data.get("updated_at", timestamp)),
            }

            results.append(file_info)

        # Validate that requested file paths were found (if file_paths was specified)
        if file_path_set is not None and len(file_path_set) > 0:
            found_paths = {str(file["file_path"]).strip() for file in results}
            missing_paths = file_path_set - found_paths

            if missing_paths:
                return json.dumps({
                    "success": False,
                    "error": f"File path(s) not found in repository '{repository_id}' branch '{branch_id}': {', '.join(sorted(missing_paths))}"
                })

        # Sort by file path for better organization
        results.sort(key=lambda x: x["file_path"])

        return json.dumps({
            "success": True,
            "count": len(results),
            "files": results
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "search_code",
                "description": (
                    "Lists files in a specific repository branch and retrieves their content. "
                    "Use this to explore the codebase structure and inspect specific files. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Required. The unique identifier of the repository to list files from."
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "Required. The unique identifier of the branch to list files from."
                        },
                        "file_paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional. List of specific file paths to retrieve (ex: [\"path_1\", \"path_2\"]). If provided, only these files will be returned. All paths must exist or an error will be returned. If omitted, all files in the branch will be returned."
                        }
                    },
                    "required": ["repository_id", "branch_id"]
                }
            }
        }
