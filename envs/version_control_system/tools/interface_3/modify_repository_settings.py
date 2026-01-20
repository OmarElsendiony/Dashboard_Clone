import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ModifyRepositorySettings(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        repository_name: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[str] = None,
        is_archived: Optional[bool] = None,
        is_template: Optional[bool] = None,
        license_type: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required to modify repository settings"})

        # Check at least one field is provided for update
        if all(v is None for v in [repository_name, description, visibility, is_archived, is_template, license_type]):
            return json.dumps({"success": False, "error": "At least one field must be provided for update"})

        repositories = data.get("repositories", {})

        # Validate repository exists
        if str(repository_id) not in repositories:
            return json.dumps({"success": False, "error": f"Repository with id '{repository_id}' not found"})

        repo = repositories[str(repository_id)]

        # Validate and update repository_name if provided
        if repository_name is not None:
            # Check new name doesn't conflict with existing repos for same owner
            for rid, r in repositories.items():
                if (rid != str(repository_id) and
                    r.get("repository_name") == repository_name and
                    str(r.get("owner_id")) == str(repo.get("owner_id")) and
                    r.get("owner_type") == repo.get("owner_type")):
                    return json.dumps({"success": False, "error": f"Repository name '{repository_name}' already exists for this owner"})
            repo["repository_name"] = repository_name

        # Update description if provided
        if description is not None:
            repo["description"] = description

        # Validate and update visibility if provided
        if visibility is not None:
            valid_visibilities = ["public", "private", "internal"]
            if visibility not in valid_visibilities:
                return json.dumps({"success": False, "error": f"Invalid visibility '{visibility}'. Valid values: public, private, internal"})
            repo["visibility"] = visibility

        # Update is_archived if provided
        if is_archived is not None:
            repo["is_archived"] = is_archived

        # Update is_template if provided
        if is_template is not None:
            repo["is_template"] = is_template

        # Validate and update license_type if provided
        if license_type is not None:
            valid_license_types = ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "unlicensed", "other"]
            if license_type not in valid_license_types:
                return json.dumps({"success": False, "error": f"Invalid license_type '{license_type}'. Valid values: MIT, Apache-2.0, GPL-3.0, BSD-3-Clause, unlicensed, other"})
            repo["license_type"] = license_type

        # Update timestamp
        repo["updated_at"] = "2026-01-01T23:59:00"

        return json.dumps({"success": True, "result": repo})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_repository_settings",
                "description": "Updates a repository's settings.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository to update."
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "The new name for the repository. Must be unique for the owner (optional)."
                        },
                        "description": {
                            "type": "string",
                            "description": "The new description for the repository (optional)."
                        },
                        "visibility": {
                            "type": "string",
                            "description": "The new visibility level. Valid values: public, private, internal (optional)."
                        },
                        "is_archived": {
                            "type": "boolean",
                            "description": "Whether the repository should be archived (optional)."
                        },
                        "is_template": {
                            "type": "boolean",
                            "description": "Whether the repository should be a template (optional)."
                        },
                        "license_type": {
                            "type": "string",
                            "description": "The new license type. Valid values: MIT, Apache-2.0, GPL-3.0, BSD-3-Clause, unlicensed, other (optional)."
                        }
                    },
                    "required": ["repository_id"]
                }
            }
        }
