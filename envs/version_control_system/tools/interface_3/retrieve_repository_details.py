import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class RetrieveRepositoryDetails(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_name: str,
        owner_name: Optional[str] = None,
        owner_type: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not repository_name:
            return json.dumps({"success": False, "error": "repository_name is required to retrieve repository details"})

        # Validate owner_type if provided
        if owner_type is not None and owner_type not in ["user", "organization"]:
            return json.dumps({"success": False, "error": f"Invalid owner_type '{owner_type}'. Valid values: user, organization"})

        repositories = data.get("repositories", {})
        users = data.get("users", {})
        organizations = data.get("organizations", {})

        # If owner_name is not provided, search by repository_name only
        if not owner_name:
            found_repo = None
            for repo_id, repo in repositories.items():
                if repo.get("repository_name") == repository_name:
                    found_repo = repo
                    break

            if not found_repo:
                return json.dumps({"success": False, "error": f"Repository '{repository_name}' not found"})

            return json.dumps({"success": True, "result": found_repo})

        # Find owner_id based on owner_type
        owner_id = None
        resolved_owner_type = owner_type

        if owner_type == "user":
            # Look up in users only
            for user_id, user in users.items():
                if user.get("username") == owner_name:
                    owner_id = user_id
                    break
            if owner_id is None:
                return json.dumps({"success": False, "error": f"User '{owner_name}' not found"})

        elif owner_type == "organization":
            # Look up in organizations only
            for org_id, org in organizations.items():
                if org.get("organization_name") == owner_name:
                    owner_id = org_id
                    break
            if owner_id is None:
                return json.dumps({"success": False, "error": f"Organization '{owner_name}' not found"})

        else:
            # owner_type not provided, check both users and organizations
            for user_id, user in users.items():
                if user.get("username") == owner_name:
                    owner_id = user_id
                    resolved_owner_type = "user"
                    break

            if owner_id is None:
                for org_id, org in organizations.items():
                    if org.get("organization_name") == owner_name:
                        owner_id = org_id
                        resolved_owner_type = "organization"
                        break

            if owner_id is None:
                return json.dumps({"success": False, "error": f"Owner '{owner_name}' not found in users or organizations"})

        # Search for repository by name and owner
        found_repo = None
        for repo_id, repo in repositories.items():
            if (repo.get("repository_name") == repository_name and
                str(repo.get("owner_id")) == str(owner_id) and
                repo.get("owner_type") == resolved_owner_type):
                found_repo = repo
                break

        if not found_repo:
            return json.dumps({"success": False, "error": f"Repository '{repository_name}' not found for owner '{owner_name}'"})

        return json.dumps({"success": True, "result": found_repo})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "retrieve_repository_details",
                "description": "Retrieves a repository's information from the version control system by looking up its name and optionally owner. The owner can be either a username (for personal repositories) or an organization name (for organization repositories).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_name": {
                            "type": "string",
                            "description": "The name of the repository to look up."
                        },
                        "owner_name": {
                            "type": "string",
                            "description": "Optional. The username of the user or organization name that owns the repository."
                        },
                        "owner_type": {
                            "type": "string",
                            "description": "The type of owner. Valid values: user, organization (optional)."
                        }
                    },
                    "required": ["repository_name"]
                }
            }
        }
