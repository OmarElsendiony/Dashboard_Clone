import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreateRepoPipeline(Tool):
   
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        pipeline_name: str,
        pipeline_path: str,
        trigger_event: str,
    ) -> str:
       

        def generate_id(table: Dict[str, Any]) -> str:
            """
            Generates a new unique ID for a record.

            Returns:
                str: The new unique ID as a string.
            """
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})
        workflows = data.get("workflows", {})

        # Validate required fields
        if not repo_id:
            return json.dumps({"success": False, "error": "Missing required parameter: repo_id"})

        if not pipeline_name:
            return json.dumps({"success": False, "error": "Missing required parameter: pipeline_name"})

        if not isinstance(pipeline_name, str) or not pipeline_name.strip():
            return json.dumps({"success": False, "error": "pipeline_name must be a non-empty string"})

        if not pipeline_path:
            return json.dumps({"success": False, "error": "Missing required parameter: pipeline_path"})

        if not isinstance(pipeline_path, str) or not pipeline_path.strip():
            return json.dumps({"success": False, "error": "pipeline_path must be a non-empty string"})

        if not trigger_event:
            return json.dumps({"success": False, "error": "Missing required parameter: trigger_event"})

        # Normalize inputs
        repo_id = str(repo_id).strip()
        pipeline_name = pipeline_name.strip()
        pipeline_path = pipeline_path.strip()

        # Validate trigger_event
        allowed_trigger_events = {"push", "pull_request", "schedule", "workflow_dispatch", "release"}
        trigger_event = trigger_event.strip().lower() if isinstance(trigger_event, str) else ""
        if trigger_event not in allowed_trigger_events:
            return json.dumps({
                "success": False,
                "error": f"trigger_event must be one of: {', '.join(sorted(allowed_trigger_events))}"
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
                "error": f"Cannot create pipeline in archived repository '{repo.get('repository_name')}'"
            })

        # Check for existing pipeline with the same name in the repository (case-insensitive)
        for _, workflow in workflows.items():
            if (
                str(workflow.get("repository_id")) == repo_id
                and workflow.get("workflow_name", "").strip().lower() == pipeline_name.lower()
            ):
                return json.dumps({
                    "success": False,
                    "error": f"Pipeline with name '{pipeline_name}' already exists in repository '{repo.get('repository_name')}'"
                })

        # Set timestamp for created_at and updated_at
        timestamp = "2026-01-01T23:59:00"

        # Generate new pipeline ID
        new_pipeline_id = generate_id(workflows)

        # Create new pipeline record
        new_pipeline = {
            "workflow_id": new_pipeline_id,
            "repository_id": repo_id,
            "workflow_name": pipeline_name,
            "workflow_path": pipeline_path,
            "trigger_event": trigger_event,
            "status": "active",
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        # Add the new pipeline to the workflows dictionary
        workflows[new_pipeline_id] = new_pipeline

        # Build the response with pipeline data using SOP terminology
        pipeline_data = {
            "pipeline_id": new_pipeline.get("workflow_id"),
            "repository_id": new_pipeline.get("repository_id"),
            "pipeline_name": new_pipeline.get("workflow_name"),
            "pipeline_path": new_pipeline.get("workflow_path"),
            "trigger_event": new_pipeline.get("trigger_event"),
            "status": new_pipeline.get("status"),
            "created_at": new_pipeline.get("created_at"),
            "updated_at": new_pipeline.get("updated_at"),
        }

        return json.dumps({
            "success": True,
            "message": f"Pipeline '{pipeline_name}' created successfully in repository '{repo.get('repository_name')}'",
            "pipeline_data": pipeline_data
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_repo_pipeline",
                "description": "Creates a new pipeline in a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository.",
                        },
                        "pipeline_name": {
                            "type": "string",
                            "description": "The name of the pipeline.",
                        },
                        "pipeline_path": {
                            "type": "string",
                            "description": "The path to the pipeline configuration file (e.g., '.github/workflows/ci.yml').",
                        },
                        "trigger_event": {
                            "type": "string",
                            "description": "The event that triggers the pipeline.",
                            "enum": ["push", "pull_request", "schedule", "workflow_dispatch", "release"]
                        },
                    },
                    "required": ["repo_id", "pipeline_name", "pipeline_path", "trigger_event"],
                },
            },
        }
