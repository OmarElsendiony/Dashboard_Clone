import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class InitializeRepository(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        owner_type: str,
        owner_id: str,
        repository_name: str,
        description: Optional[str] = None,
        visibility: Optional[str] = "public",
        default_branch: Optional[str] = "main",
        is_template: Optional[bool] = False,
        license_type: Optional[str] = None
    ) -> str:
        """
        Creates a new repository in the version control system.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not owner_type:
            return json.dumps({"success": False, "error": "owner_type is required to initialize repository"})
        if not owner_id:
            return json.dumps({"success": False, "error": "owner_id is required to initialize repository"})
        if not repository_name:
            return json.dumps({"success": False, "error": "repository_name is required to initialize repository"})

        # Typecast string parameters for safety
        owner_type = str(owner_type).strip()
        owner_id = str(owner_id).strip()
        repository_name = str(repository_name).strip()
        description = str(description).strip() if description is not None else None
        visibility = str(visibility).strip() if visibility is not None else "public"
        default_branch = str(default_branch).strip() if default_branch is not None else "main"
        license_type = str(license_type).strip() if license_type is not None else None

        # Validate and typecast is_template
        if is_template is not None:
            if isinstance(is_template, bool):
                pass  # Already boolean
            elif isinstance(is_template, str):
                if is_template.lower() == "true":
                    is_template = True
                elif is_template.lower() == "false":
                    is_template = False
                else:
                    return json.dumps({"success": False, "error": f"Invalid is_template '{is_template}'. Valid values: true, false, True, False"})
            else:
                return json.dumps({"success": False, "error": f"Invalid is_template '{is_template}'. Valid values: true, false, True, False"})
        else:
            is_template = False

        # Validate owner_type
        valid_owner_types = ["user", "organization"]
        if owner_type not in valid_owner_types:
            return json.dumps({"success": False, "error": f"Invalid owner_type '{owner_type}'. Valid values: user, organization"})

        # Validate visibility
        valid_visibilities = ["public", "private", "internal"]
        if visibility not in valid_visibilities:
            return json.dumps({"success": False, "error": f"Invalid visibility '{visibility}'. Valid values: public, private, internal"})

        # Validate license_type if provided
        if license_type is not None:
            valid_license_types = ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "unlicensed", "other"]
            if license_type not in valid_license_types:
                return json.dumps({"success": False, "error": f"Invalid license_type '{license_type}'. Valid values: MIT, Apache-2.0, GPL-3.0, BSD-3-Clause, unlicensed, other"})

        repositories = data.get("repositories", {})
        users = data.get("users", {})
        organizations = data.get("organizations", {})
        branches = data.get("branches", {})

        # Validate owner exists
        if owner_type == "user":
            if str(owner_id) not in users:
                return json.dumps({"success": False, "error": f"User with id '{owner_id}' not found"})
        else:
            if str(owner_id) not in organizations:
                return json.dumps({"success": False, "error": f"Organization with id '{owner_id}' not found"})

        # Check repository name doesn't already exist for this owner
        for repo_id, repo in repositories.items():
            if (repo.get("repository_name") == repository_name and
                str(repo.get("owner_id")) == str(owner_id) and
                repo.get("owner_type") == owner_type):
                return json.dumps({"success": False, "error": f"Repository '{repository_name}' already exists for this owner"})

        # Generate new repository_id
        if repositories:
            max_id = max(int(k) for k in repositories.keys())
            new_id = str(max_id + 1)
        else:
            new_id = "1"

        # Create repository record
        new_repo = {
            "repository_id": new_id,
            "owner_type": owner_type,
            "owner_id": owner_id,
            "project_id": None,
            "repository_name": repository_name,
            "description": description,
            "visibility": visibility,
            "default_branch": default_branch,
            "is_fork": False,
            "parent_repository_id": None,
            "is_archived": False,
            "is_template": is_template,
            "stars_count": 0,
            "forks_count": 0,
            "license_type": license_type,
            "created_at": "2026-01-01T23:59:00",
            "updated_at": "2026-01-01T23:59:00",
            "pushed_at": None
        }

        repositories[new_id] = new_repo

        # Create default branch entry
        if branches:
            max_branch_id = max(int(k) for k in branches.keys())
            new_branch_id = str(max_branch_id + 1)
        else:
            new_branch_id = "1"


        new_branch = {
            "branch_id": new_branch_id,
            "repository_id": new_id,
            "branch_name": default_branch,
            "commit_sha": None,
            "source_branch": None,
            "is_default": True,
            "created_at": "2026-01-01T23:59:00",
            "updated_at": "2026-01-01T23:59:00"
        }

        branches[new_branch_id] = new_branch

        return json.dumps({"success": True, "result": {"repository": new_repo, "default_branch": new_branch}})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "initialize_repository",
                "description": "Creates a new repository in the version control system. The repository name must be unique for the specified owner.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "owner_type": {
                            "type": "string",
                            "description": "The type of owner for the repository. Valid values: user, organization."
                        },
                        "owner_id": {
                            "type": "string",
                            "description": "The unique identifier of the owner (user_id or organization_id)."
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "The name for the new repository. Must be unique for the owner."
                        },
                        "description": {
                            "type": "string",
                            "description": "A text description of the repository. Optional."
                        },
                        "visibility": {
                            "type": "string",
                            "description": "The visibility level of the repository. Valid values: public, private, internal. Default: public."
                        },
                        "default_branch": {
                            "type": "string",
                            "description": "The name of the default branch. Default: main."
                        },
                        "is_template": {
                            "type": "boolean",
                            "description": "Whether this repository is a template repository. Default: false. Valid values: true, false, True, False."
                        },
                        "license_type": {
                            "type": "string",
                            "description": "The license type for the repository. Valid values: MIT, Apache-2.0, GPL-3.0, BSD-3-Clause, unlicensed, other. Optional."
                        }
                    },
                    "required": ["owner_type", "owner_id", "repository_name"]
                }
            }
        }
