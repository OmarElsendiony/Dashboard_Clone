import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdatePipeline(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        pipeline_name: str,
        action: str,
        pipeline_path: Optional[str] = None,
        trigger_event: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})
        workflows = data.get("workflows", {})
        files = data.get("files", {})

        # Validate required fields
        if not repo_id or not str(repo_id).strip():
            return json.dumps({"success": False, "error": "repo_id must be provided"})

        if not pipeline_name:
            return json.dumps({"success": False, "error": "pipeline_name must be provided"})

        if not isinstance(pipeline_name, str) or not pipeline_name.strip():
            return json.dumps({"success": False, "error": "pipeline_name must be a non-empty string"})

        if not action:
            return json.dumps({"success": False, "error": "action must be provided"})

        if not isinstance(action, str):
            return json.dumps({"success": False, "error": "action must be a string"})

        # Normalize inputs
        repo_id = str(repo_id).strip()
        pipeline_name = pipeline_name.strip()
        action = action.strip().lower()

        # Validate action
        allowed_actions = {"update", "enable", "disable"}
        if action not in allowed_actions:
            return json.dumps({
                "success": False,
                "error": f"action must be one of: {', '.join(sorted(allowed_actions))}"
            })

        # Validate repository exists
        repo = None
        for _, r in repositories.items():
            if str(r.get("repository_id")) == repo_id:
                repo = r
                break

        if not repo:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repo_id}' not found"
            })

        # Check if repository is archived
        if repo.get("is_archived"):
            return json.dumps({
                "success": False,
                "error": f"Cannot update pipeline in archived repository '{repo.get('repository_name')}'"
            })

        # Find the pipeline by repository_id and pipeline_name (case-insensitive)
        found_pipeline = None
        for _, workflow in workflows.items():
            if (
                str(workflow.get("repository_id")) == repo_id
                and workflow.get("workflow_name", "").strip().lower() == pipeline_name.lower()
            ):
                found_pipeline = workflow
                break

        if not found_pipeline:
            return json.dumps({
                "success": False,
                "error": f"Pipeline '{pipeline_name}' not found in repository '{repo_id}'"
            })

        # Track if any updates were made
        updates_applied = False
        timestamp = "2026-01-01T23:59:00"

        # Handle different actions
        if action == "update":
            # For update action, at least one of pipeline_path or trigger_event must be provided
            if pipeline_path is None and trigger_event is None:
                return json.dumps({
                    "success": False,
                    "error": "For 'update' action, at least one of pipeline_path or trigger_event must be provided"
                })

            # Validate and apply pipeline_path update
            if pipeline_path is not None:
                if not isinstance(pipeline_path, str) or not pipeline_path.strip():
                    return json.dumps({"success": False, "error": "pipeline_path must be a non-empty string"})
                pipeline_path = pipeline_path.strip()

                # Ensure the new pipeline file exists in the repository
                file_found = False
                for _, file_record in files.items():
                    if (
                        str(file_record.get("repository_id")) == repo_id
                        and file_record.get("file_path", "").strip() == pipeline_path
                    ):
                        file_found = True
                        break

                if not file_found:
                    return json.dumps({
                        "success": False,
                        "error": f"Pipeline file '{pipeline_path}' not found in repository '{repo.get('repository_name')}'"
                    })

                found_pipeline["workflow_path"] = pipeline_path
                updates_applied = True

            # Validate and apply trigger_event update
            if trigger_event is not None:
                allowed_trigger_events = {
                    "push", "pull_request", "schedule", "workflow_dispatch", "release"}
                if not isinstance(trigger_event, str):
                    return json.dumps({"success": False, "error": "trigger_event must be a string"})
                trigger_event_val = trigger_event.strip().lower()
                if trigger_event_val not in allowed_trigger_events:
                    return json.dumps({
                        "success": False,
                        "error": f"trigger_event must be one of: {', '.join(sorted(allowed_trigger_events))}"
                    })
                found_pipeline["trigger_event"] = trigger_event_val
                updates_applied = True

        elif action == "enable":
            # Set status to active
            found_pipeline["status"] = "active"
            updates_applied = True

        elif action == "disable":
            # Set status to disabled
            found_pipeline["status"] = "disabled"
            updates_applied = True

        if not updates_applied:
            return json.dumps({
                "success": False,
                "error": "No updates applied"
            })

        # Update the updated_at timestamp
        found_pipeline["updated_at"] = timestamp

        # Build the response with updated pipeline data
        pipeline_data = {
            "pipeline_id": found_pipeline.get("workflow_id"),
            "repository_id": found_pipeline.get("repository_id"),
            "pipeline_name": found_pipeline.get("workflow_name"),
            "pipeline_path": found_pipeline.get("workflow_path"),
            "trigger_event": found_pipeline.get("trigger_event"),
            "status": found_pipeline.get("status"),
            "created_at": found_pipeline.get("created_at"),
            "updated_at": found_pipeline.get("updated_at"),
        }

        return json.dumps({
            "success": True,
            "message": f"Pipeline '{pipeline_name}' {action}d successfully in repository '{repo.get('repository_name')}'",
            "pipeline_data": pipeline_data
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:

        return {
            "type": "function",
            "function": {
                "name": "update_pipeline",
                "description": "Updates, enables, or disables a pipeline (workflow) in a repository in the version control system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository containing the pipeline.",
                        },
                        "pipeline_name": {
                            "type": "string",
                            "description": "The name of the pipeline to update.",
                        },
                        "action": {
                            "type": "string",
                            "description": "The action to perform.",
                            "enum": ["update", "enable", "disable"]
                        },
                        "pipeline_path": {
                            "type": "string",
                            "description": "The new path to the pipeline configuration file (e.g., '.github/workflows/ci.yml'). Optional field, required for 'update' action if trigger_event is not provided.",
                        },
                        "trigger_event": {
                            "type": "string",
                            "description": "The new trigger event for the pipeline. Optional field, required for 'update' action if pipeline_path is not provided.",
                            "enum": ["push", "pull_request", "schedule", "workflow_dispatch", "release"]
                        },
                    },
                    "required": ["repo_id", "pipeline_name", "action"],
                },
            },
        }
