import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class RegisterWorkflow(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        branch_id: str,
        workflow_name: str,
        workflow_path: str,
        trigger_event: str,
        status: Optional[str] = None
    ) -> str:
        """
        Registers a new CI/CD workflow in a repository.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required to register a workflow"})
        if not branch_id:
            return json.dumps({"success": False, "error": "branch_id is required to register a workflow"})
        if not workflow_name:
            return json.dumps({"success": False, "error": "workflow_name is required to register a workflow"})
        if not workflow_path:
            return json.dumps({"success": False, "error": "workflow_path is required to register a workflow"})
        if not trigger_event:
            return json.dumps({"success": False, "error": "trigger_event is required to register a workflow"})

        # Validate trigger_event
        valid_trigger_events = ["push", "pull_request", "schedule", "workflow_dispatch", "release"]
        if trigger_event not in valid_trigger_events:
            return json.dumps({"success": False, "error": f"Invalid trigger_event '{trigger_event}'. Valid values: push, pull_request, schedule, workflow_dispatch, release"})

        # Set default status if not provided
        if status is None:
            status = "active"

        # Validate status
        valid_statuses = ["active", "disabled", "deleted"]
        if status not in valid_statuses:
            return json.dumps({"success": False, "error": f"Invalid status '{status}'. Valid values: active, disabled, deleted"})

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        files = data.get("files", {})
        workflows = data.get("workflows", {})

        # Validate repository exists
        if str(repository_id) not in repositories:
            return json.dumps({"success": False, "error": f"Repository with id '{repository_id}' not found"})

        # Validate branch exists
        if str(branch_id) not in branches:
            return json.dumps({"success": False, "error": f"Branch with id '{branch_id}' not found"})

        branch = branches[str(branch_id)]

        # Validate branch belongs to the repository
        if str(branch.get("repository_id")) != str(repository_id):
            return json.dumps({"success": False, "error": f"Branch '{branch_id}' does not belong to repository '{repository_id}'"})

        # Validate workflow_path exists as a file in this repository and branch
        file_found = False
        for file_id, file in files.items():
            if (str(file.get("repository_id")) == str(repository_id) and
                str(file.get("branch_id")) == str(branch_id) and
                file.get("file_path") == workflow_path):
                file_found = True
                break

        if not file_found:
            return json.dumps({"success": False, "error": f"File '{workflow_path}' not found in repository '{repository_id}' on branch '{branch_id}'"})

        # Generate new workflow_id
        if workflows:
            max_id = max(int(k) for k in workflows.keys())
            new_workflow_id = str(max_id + 1)
        else:
            new_workflow_id = "1"

        # Create workflow record
        new_workflow = {
            "workflow_id": new_workflow_id,
            "repository_id": repository_id,
            "workflow_name": workflow_name,
            "workflow_path": workflow_path,
            "trigger_event": trigger_event,
            "status": status,
            "created_at": "2026-01-01T23:59:00",
            "updated_at": "2026-01-01T23:59:00"
        }

        workflows[new_workflow_id] = new_workflow

        return json.dumps({"success": True, "result": new_workflow})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "register_workflow",
                "description": "Registers a new CI/CD workflow in a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository where the workflow will be registered."
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "The unique identifier of the branch where the workflow file exists."
                        },
                        "workflow_name": {
                            "type": "string",
                            "description": "The name of the workflow."
                        },
                        "workflow_path": {
                            "type": "string",
                            "description": "The file path to the workflow configuration file (e.g., .github/workflows/ci.yml). Must exist in the repository on the specified branch."
                        },
                        "trigger_event": {
                            "type": "string",
                            "description": "The event that triggers the workflow. Valid values: push, pull_request, schedule, workflow_dispatch, release."
                        },
                        "status": {
                            "type": "string",
                            "description": "The initial status of the workflow. Valid values: active, disabled, deleted. Default: active."
                        }
                    },
                    "required": ["repository_id", "branch_id", "workflow_name", "workflow_path", "trigger_event"]
                }
            }
        }
