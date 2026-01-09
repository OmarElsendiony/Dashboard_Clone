import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class CreateWorkflow(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        repository_id: str,
        workflow_name: str,
        workflow_path: str,
        trigger_event: str,
        status: str = 'active'
    ) -> str:
        """
        Creates a new CI/CD workflow for a repository, enforcing permission checks.
        """
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        timestamp = "2026-01-01T23:59:00"

        try:
            encoded_input_token = base64.b64encode(access_token.encode('utf-8')).decode('utf-8')
        except Exception:
            return json.dumps({"error": "Failed to process access token"})

        tokens = data.get("access_tokens", {})
        user_id = None
        
        for token in tokens.values():
            if token.get("token_encoded") == encoded_input_token and token.get("status") == "active":
                if token.get("expires_at") > timestamp:
                    user_id = token.get("user_id")
                    break
        
        if not user_id:
            return json.dumps({"error": "Invalid or expired access token"})

        repositories = data.get("repositories", {})
        if repository_id not in repositories:
            return json.dumps({"error": f"Repository {repository_id} not found"})

        repo = repositories[repository_id]
        
  
        has_permission = False
        
        if repo.get("owner_type") == 'user' and repo.get("owner_id") == user_id:
            has_permission = True
        
        if not has_permission and repo.get("owner_type") == 'organization':
            org_members = data.get("organization_members", {})
            for member in org_members.values():
                if (member.get("organization_id") == repo.get("owner_id") and 
                    member.get("user_id") == user_id and 
                    member.get("status") == "active" and 
                    member.get("role") == "owner"):
                    has_permission = True
                    break

        if not has_permission:
            collaborators = data.get("repository_collaborators", {})
            for collab in collaborators.values():
                if (collab.get("repository_id") == repository_id and 
                    collab.get("user_id") == user_id and 
                    collab.get("status") == "active" and 
                    collab.get("permission_level") in ['write', 'admin']):
                    has_permission = True
                    break
        
        if not has_permission:
            return json.dumps({"error": "User does not have permission to create workflows in this repository"})

        # QA Correction: Update valid trigger events
        valid_events = ['push', 'pull_request', 'schedule']
        if trigger_event not in valid_events:
            return json.dumps({"error": f"Invalid trigger_event. Must be one of: {', '.join(valid_events)}"})

        # QA Correction: Update valid status values to match 'user_status' enum
        valid_statuses = ['active', 'suspended', 'deleted']
        if status not in valid_statuses:
            return json.dumps({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"})

        # Create Workflow
        workflows = data.get("workflows", {})
        new_id = generate_id(workflows)
        new_workflow = {
            "workflow_id": new_id,
            "repository_id": repository_id,
            "workflow_name": workflow_name,
            "workflow_path": workflow_path,
            "trigger_event": trigger_event,
            "status": status,
            "created_at": timestamp,
            "updated_at": timestamp
        }

        workflows[new_id] = new_workflow
        return json.dumps(new_workflow)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_workflow",
                "description": "Creates a new workflow definition for a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "The access token for authentication."
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository."
                        },
                        "workflow_name": {
                            "type": "string",
                            "description": "The name of the workflow."
                        },
                        "workflow_path": {
                            "type": "string",
                            "description": "The path to the workflow file (e.g., .github/workflows/main.yml)."
                        },
                        "trigger_event": {
                            "type": "string",
                            "description": "The event that triggers the workflow. Allowed values: 'push', 'pull_request', 'schedule'."
                        },
                        "status": {
                            "type": "string",
                            "description": "The initial status of the workflow. Allowed values: 'active', 'suspended', 'deleted'. Default is 'active'."
                        }
                    },
                    "required": ["access_token", "repository_id", "workflow_name", "workflow_path", "trigger_event"]
                }
            }
        }