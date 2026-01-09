import json
from typing import Any, Dict, Optional, Tuple
from tau_bench.envs.tool import Tool


class UpdateProject(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: str,
        workspace_id: str,
        project_key: Optional[str] = None,
        project_name: Optional[str] = None,
        description: Optional[str] = None,
        is_private: Optional[bool] = None,
    ) -> str:
        """Update project information."""
        timestamp = "2026-01-01T23:59:00"
        def check_uniqueness(projects_dict: Dict[str, Any], workspace_id_str: str, project_id_str: str, project_key_str: Optional[str], project_name_str: Optional[str]) -> Tuple[bool, Optional[str]]:
            """Check if project_key and project_name are unique within the workspace, excluding current project."""
            for pid, project in projects_dict.items():
                if str(pid) == project_id_str:
                    continue
                
                if str(project.get("workspace_id")) != workspace_id_str:
                    continue
                
                if project_key_str and str(project.get("project_key", "")).strip() == project_key_str:
                    return False, f"Project with key '{project_key_str}' already exists in workspace '{workspace_id_str}' (project_id: {pid})"
                
                if project_name_str and str(project.get("project_name", "")).strip() == project_name_str:
                    return False, f"Project with name '{project_name_str}' already exists in workspace '{workspace_id_str}' (project_id: {pid})"
            
            return True, None

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})
        
        if str(is_private) not in ["True", "False"]:
            return json.dumps({"success": False, "error": "Invalid input value. Expected True or False"})

        # Check at least one update parameter is provided
        if not project_key and not project_name and not description and is_private is None:
            return json.dumps({
                "success": False,
                "error": "At least one of project_key, project_name, description, or is_private must be provided for update"
            })

        # Get data containers
        projects_dict = data.get("projects", {})

        # Convert to strings
        project_id_str = str(project_id).strip()
        workspace_id_str = str(workspace_id).strip()
        project_key_str = str(project_key).strip() if project_key else None
        project_name_str = str(project_name).strip() if project_name else None

        # Check if project exists
        if project_id_str not in projects_dict:
            return json.dumps({
                "success": False,
                "error": f"Project with ID '{project_id_str}' not found"
            })

        project = projects_dict[project_id_str]

        # Check uniqueness
        is_valid, error_msg = check_uniqueness(projects_dict, workspace_id_str, project_id_str, project_key_str, project_name_str)
        if not is_valid:
            return json.dumps({"success": False, "error": error_msg})

        if project_key_str:
            project["project_key"] = project_key_str

        if project_name_str:
            project["project_name"] = project_name_str

        if description is not None:
            project["description"] = str(description).strip()

        if is_private is not None:
            project["is_private"] = bool(is_private)

        project["updated_at"] = timestamp

        project_return = project.copy()
        project_return["project_id"] = project_id_str

        return json.dumps({
            "success": True,
            "project": project_return,
            "message": f"Project '{project.get('project_name')}' updated successfully",
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the update_project function."""
        return {
            "type": "function",
            "function": {
                "name": "update_project",
                "description": (
                    "Update project information including project_key, project_name, description, and privacy settings. "
                    "At least one of project_key, project_name, description, or is_private must be provided for update. "
                    "Validates that the project exists. "
                    "If project_key is provided, ensures it's unique within the workspace (excluding the current project). "
                    "If project_name is provided, ensures it's unique within the workspace (excluding the current project). "
                    "Returns the updated project details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The ID of the project to update.",
                        },
                        "workspace_id": {
                            "type": "string",
                            "description": "The ID of the workspace containing the project.",
                        },
                        "project_key": {
                            "type": "string",
                            "description": "Optional. The new unique key for the project within the workspace.",
                        },
                        "project_name": {
                            "type": "string",
                            "description": "Optional. The new unique name for the project within the workspace.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional. The new description for the project.",
                        },
                        "is_private": {
                            "type": "boolean",
                            "description": "Optional. Whether the project is private.",
                        },
                    },
                    "required": ["project_id", "workspace_id"],
                },
            },
        }