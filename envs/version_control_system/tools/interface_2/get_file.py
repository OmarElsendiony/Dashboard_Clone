import json
from typing import Any, Dict, Optional, Tuple
from tau_bench.envs.tool import Tool


class GetFile(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        branch_id: str,
        file_name: str,
        file_path: str,
    ) -> str:
        """Retrieve file information and content by repository_id, branch_id, file_name, and file_path."""

        def find_file(files_dict: Dict[str, Any], repository_id_str: str, branch_id_str: str, file_name_str: str, file_path_str: str) -> Optional[Dict[str, Any]]:
            """Find file by repository_id, branch_id, file_name, and file_path."""
            for fid, file in files_dict.items():

                if (str(file.get("repository_id")) == repository_id_str and 
                    str(file.get("branch_id")) == branch_id_str and 
                    str(file.get("file_name", "")).strip() == file_name_str and 
                    str(file.get("file_path", "")).strip() == file_path_str):
                    file_info = file.copy()
                    file_info["file_id"] = str(fid)
                    return file_info
            
            return None

        def find_file_content(file_contents_dict: Dict[str, Any], file_id: str) -> Optional[Dict[str, Any]]:
            """Find file content by file_id."""
            for cid, content in file_contents_dict.items():
                
                if str(content.get("file_id")) == file_id:
                    content_info = content.copy()
                    content_info["content_id"] = str(cid)
                    return content_info
            
            return None

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        files_dict = data.get("files", {})
        file_contents_dict = data.get("file_contents", {})

        repository_id_str = str(repository_id).strip()
        branch_id_str = str(branch_id).strip()
        file_name_str = str(file_name).strip()
        file_path_str = str(file_path).strip()

        file = find_file(files_dict, repository_id_str, branch_id_str, file_name_str, file_path_str)

        if not file:
            return json.dumps({
                "success": False,
                "error": f"File '{file_name_str}' at path '{file_path_str}' not found in repository '{repository_id_str}' on branch '{branch_id_str}'"
            })

        # Find file content
        file_content = find_file_content(file_contents_dict, file["file_id"])

        return json.dumps({
            "success": True,
            "file": file,
            "file_content": file_content,
            "message": f"File '{file_name_str}' at path '{file_path_str}' found in repository '{repository_id_str}' on branch '{branch_id_str}'",
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the get_file function."""
        return {
            "type": "function",
            "function": {
                "name": "get_file",
                "description": (
                    "Retrieve file information and content by repository_id, branch_id, file_name, and file_path. "
                    "Returns complete file details including file_id, repository_id, branch_id, directory_id, "
                    "file_path, file_name, language, is_binary, last_modified_at, last_commit_id, and timestamps. "
                    "Also returns file content details including content_id, file_id, commit_id, content, encoding, and created_at. "
                    "The file_content field will be null if no content is found for the file. "
                    "Returns an error if any required parameter is not provided or if the file is not found."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository containing the file.",
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "The ID of the branch containing the file.",
                        },
                        "file_name": {
                            "type": "string",
                            "description": "The name of the file to retrieve.",
                        },
                        "file_path": {
                            "type": "string",
                            "description": "The path of the file to retrieve.",
                        },
                    },
                    "required": ["repository_id", "branch_id", "file_name", "file_path"],
                },
            },
        }