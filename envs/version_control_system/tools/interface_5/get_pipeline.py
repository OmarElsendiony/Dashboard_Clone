import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetPipeline(Tool):
    """Tool for retrieving pipeline (workflow) details from the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        pipeline_name: str,
    ) -> str:
        """
        Retrieve pipeline details by repository ID and pipeline name.

        Args:
            data: The data dictionary containing all version control system data.
            repo_id: The ID of the repository containing the pipeline (required).
            pipeline_name: The name of the pipeline to look up (required).

        Returns:
            JSON string containing the success status and pipeline data if found.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        workflows = data.get("workflows", {})
        repositories = data.get("repositories", {})

        # Validate required fields
        if not repo_id or not str(repo_id).strip():
            return json.dumps({"success": False, "error": "repo_id must be provided"})

        if not pipeline_name:
            return json.dumps({"success": False, "error": "pipeline_name must be provided"})

        if not isinstance(pipeline_name, str) or not pipeline_name.strip():
            return json.dumps({"success": False, "error": "pipeline_name must be a non-empty string"})

        # Normalize inputs
        repo_id = str(repo_id).strip()
        pipeline_name = pipeline_name.strip()

        # Validate repository exists
        repo_found = False
        for _, repo in repositories.items():
            if str(repo.get("repository_id")) == repo_id:
                repo_found = True
                break

        if not repo_found:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repo_id}' not found"
            })

        # Search for pipeline by repository_id and workflow_name (case-insensitive)
        found_pipeline = None
        for _, workflow in workflows.items():
            if (
                str(workflow.get("repository_id")) == repo_id
                and workflow.get("workflow_name", "").strip().lower() == pipeline_name.lower()
            ):
                found_pipeline = workflow.copy()
                break

        if not found_pipeline:
            return json.dumps({
                "success": False,
                "error": f"Pipeline '{pipeline_name}' not found in repository '{repo_id}'"
            })

        # Build the response with pipeline data
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
            "pipeline_data": pipeline_data
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the get_pipeline function."""
        return {
            "type": "function",
            "function": {
                "name": "get_pipeline",
                "description": "Retrieves detailed information about a pipeline from a repository by repository ID and pipeline name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository containing the pipeline.",
                        },
                        "pipeline_name": {
                            "type": "string",
                            "description": "The name of the pipeline to look up.",
                        },
                    },
                    "required": ["repo_id", "pipeline_name"],
                },
            },
        }
