import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class DeleteWorkflow(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        workflow_id: str
    ) -> str:
        """
        Permanently deletes a workflow.
        """
        timestamp = "2025-10-01T00:00:00"

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

        workflows = data.get("workflows", {})

        if workflow_id not in workflows:
            return json.dumps({"error": f"Workflow {workflow_id} not found"})

        deleted_workflow = workflows.pop(workflow_id)
        # successful deletion message
        deleted_workflow["message"] = f"Workflow {workflow_id} has been successfully deleted."
        return json.dumps(deleted_workflow)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "delete_workflow",
                "description": "Permanently deletes a workflow record.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "The access token for authentication."
                        },
                        "workflow_id": {
                            "type": "string",
                            "description": "The ID of the workflow to delete."
                        }
                    },
                    "required": ["access_token", "workflow_id"]
                }
            }
        }