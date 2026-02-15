import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class DeleteIssue(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        issue_id: str
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        issues = data.get("issues", {})
        if issue_id not in issues:
            return json.dumps({
                "success": False,
                "error": f"Issue with ID '{issue_id}' does not exist"
            })
        deleted_issue = issues.get(issue_id, None)
        del issues[issue_id]
        return json.dumps({"success": True, "deleted_issue": deleted_issue})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "delete_issue",
                "description": "Permanently removes a specified issue from the tracking system. Use with caution as the operation is destructive and cannot be undone. Use this to clean up duplicate, erroneous, or resolved issues that no longer require a record.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string",
                            "description": "The ID of the issue to be deleted."
                        }
                    },
                    "required": ["issue_id"]
                }
            }
        }
