import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateWorkflow(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        workflow_id: str,
        workflow_name: Optional[str] = None,
        workflow_path: Optional[str] = None,
        trigger_event: Optional[str] = None,
        status: Optional[str] = None
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

        workflows = data.get("workflows", {})

        if workflow_id not in workflows:
            return json.dumps({"error": f"Workflow {workflow_id} not found"})

        workflow = workflows[workflow_id]

        valid_events = ['push', 'pull_request', 'schedule', 'workflow_dispatch', 'release']
        if trigger_event and trigger_event not in valid_events:
            return json.dumps({"error": f"Invalid trigger_event. Must be one of: {', '.join(valid_events)}"})

        valid_statuses = ['active', 'disabled', 'deleted']
        if status and status not in valid_statuses:
            return json.dumps({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"})

        if workflow_name is not None:
            workflow["workflow_name"] = workflow_name
        if workflow_path is not None:
            workflow["workflow_path"] = workflow_path
        if trigger_event is not None:
            workflow["trigger_event"] = trigger_event
        if status is not None:
            workflow["status"] = status

        workflow["updated_at"] = timestamp
        workflows[workflow_id] = workflow

        return json.dumps(workflow)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_workflow",
                "description": "Updates the configuration of an existing workflow.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "The access token for authentication."
                        },
                        "workflow_id": {
                            "type": "string",
                            "description": "The ID of the workflow to update."
                        },
                        "workflow_name": {
                            "type": "string",
                            "description": "The new name of the workflow (optional)"
                        },
                        "workflow_path": {
                            "type": "string",
                            "description": "The new file path to the workflow definition (optional)"
                        },
                        "trigger_event": {
                            "type": "string",
                            "description": "The event that triggers the workflow. Allowed values: 'push', 'pull_request', 'schedule', 'workflow_dispatch', 'release' (optional)",
                            "enum": ["push", "pull_request", "schedule", "workflow_dispatch", "release"]
                        },
                        "status": {
                            "type": "string",
                            "description": "The new status of the workflow. Allowed values: 'active', 'disabled', 'deleted' (optional)",
                            "enum": ["active", "disabled", "deleted"]
                        }
                    },
                    "required": ["access_token", "workflow_id"]
                }
            }
        }