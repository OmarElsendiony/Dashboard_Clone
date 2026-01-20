import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class DissolveOrganization(Tool):

    @staticmethod
    def invoke(data: Dict[str, Any], organization_id: str) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not organization_id:
            return json.dumps({"success": False, "error": "organization_id is required to dissolve an organization"})

        organizations = data.get("organizations", {})
        organization_members = data.get("organization_members", {})
        repositories = data.get("repositories", {})

        # Validate organization exists
        if str(organization_id) not in organizations:
            return json.dumps({"success": False, "error": f"Organization with id '{organization_id}' not found"})

        # Get the organization record before deletion
        deleted_org = organizations[str(organization_id)]

        # Remove all organization memberships
        memberships_to_remove = []
        for membership_id, membership in organization_members.items():
            if str(membership.get("organization_id")) == str(organization_id):
                memberships_to_remove.append(membership_id)
        for membership_id in memberships_to_remove:
            del organization_members[membership_id]

        # Remove all repositories owned by this organization
        repos_to_remove = []
        for repo_id, repo in repositories.items():
            if (repo.get("owner_type") == "organization" and
                str(repo.get("owner_id")) == str(organization_id)):
                repos_to_remove.append(repo_id)
        for repo_id in repos_to_remove:
            del repositories[repo_id]

        # Delete the organization
        del organizations[str(organization_id)]

        return json.dumps({
            "success": True,
            "result": deleted_org,
            "message": f"Organization '{deleted_org.get('organization_name')}' has been deleted along with {len(memberships_to_remove)} memberships and {len(repos_to_remove)} repositories"
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "dissolve_organization",
                "description": "Deletes an organization from the version control system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "organization_id": {
                            "type": "string",
                            "description": "The unique identifier of the organization to delete."
                        }
                    },
                    "required": ["organization_id"]
                }
            }
        }
