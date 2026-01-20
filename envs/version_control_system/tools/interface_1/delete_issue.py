import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class DeleteIssue(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        issue_id: str
    ) -> str:
        timestamp = "2026-01-01T23:59:00"
       
        try:
            encoded_input_token = base64.b64encode(access_token.encode('utf-8')).decode('utf-8')
        except Exception:
            return json.dumps({"error": "Failed to process access token"})

        tokens = data.get("access_tokens", {})
        valid_token = False
        for token in tokens.values():
            if token.get("token_encoded") == encoded_input_token and token.get("status") == "active":
                if token.get("expires_at") > timestamp:
                    valid_token = True
                    break
        
        if not valid_token:
            return json.dumps({"error": "Invalid or expired access token"})

        issues = data.get("issues", {})

        if issue_id not in issues:
            return json.dumps({"error": f"Issue {issue_id} not found"})

        deleted_issue = issues.pop(issue_id)
        return json.dumps(deleted_issue)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "delete_issue",
                "description": "Deletes an issue by ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "The access token for authentication."
                        },
                        "issue_id": {
                            "type": "string",
                            "description": "The ID of the issue to delete."
                        }
                    },
                    "required": ["access_token", "issue_id"]
                }
            }
        }