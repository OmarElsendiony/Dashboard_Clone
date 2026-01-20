import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class RemoveFile(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        file_id: str,
    ) -> str:

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        # Get data containers
        files_dict = data.get("files", {})
        file_contents_dict = data.get("file_contents", {})

        # Convert to string
        file_id_str = str(file_id).strip()

        # Validate file exists
        if file_id_str not in files_dict:
            return json.dumps({
                "success": False,
                "error": f"File with ID '{file_id_str}' not found",
            })

        file_info = files_dict[file_id_str].copy()
        file_name = file_info.get("file_name", "")

        # Delete all file_contents records for this file
        deleted_content_count = 0
        for content_id in list(file_contents_dict.keys()):
            if isinstance(file_contents_dict[content_id], dict) and str(file_contents_dict[content_id].get("file_id")) == file_id_str:
                del file_contents_dict[content_id]
                deleted_content_count += 1

        # Delete file
        del files_dict[file_id_str]

        return json.dumps({
            "success": True,
            "deleted_file": file_info,
            "message": f"File '{file_name}' and {deleted_content_count} content version(s) deleted successfully",
            "deleted_counts": {
                "file_contents": deleted_content_count,
            }
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        
        return {
            "type": "function",
            "function": {
                "name": "remove_file",
                "description": (
                    "Removes a file after validating its existence. Deletes the file and all associated file content versions, do not delete any commits, and returns the deleted file information along with the count of removed file content records."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_id": {
                            "type": "string",
                            "description": "The ID of the file to remove.",
                        },
                    },
                    "required": ["file_id"],
                },
            },
        }
