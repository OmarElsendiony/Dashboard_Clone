import json
from typing import Dict, Optional
from tau_bench.envs.tool import Tool


class ListUsers(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, object],
        status: str,
        repository_id: Optional[str] = None,
        role: Optional[str] = None,
        technical_expertise: Optional[str] = None,
        user_identifier_type: Optional[str] = None,
        user_identifier: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for users"}
            )

        if not status:
            return json.dumps({"success": False, "error": "status is required"})

        repositories = data.get("repositories", {})
        users = data.get("users", {})

        if repository_id:
            if repository_id not in repositories.keys():
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Repository with ID {repository_id} not found",
                    }
                )

            # Collect user IDs associated with this repository through pull requests
            associated_user_ids = set()
            pull_requests = data.get("pull_requests", {})
            for pr_data in pull_requests.values():
                if str(pr_data.get("repository_id")) == str(repository_id):
                    author_id = pr_data.get("author_id")
                    if author_id:
                        associated_user_ids.add(str(author_id))
                    team_lead_id = pr_data.get("assigned_team_lead")
                    if team_lead_id:
                        associated_user_ids.add(str(team_lead_id))
        else:
            associated_user_ids = None

        valid_roles = ["technical_engineer", "support_engineer"]
        if role and role not in valid_roles:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid role '{role}'. Must be one of: {', '.join(valid_roles)}",
                }
            )

        valid_statuses = ["active", "inactive"]
        if status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                }
            )

        results = []

        for uid, user_data in users.items():
            # FIX: Correct logic to handle retrieval by username or email
            if user_identifier:
                if not user_identifier_type:
                    return json.dumps(
                        {"success": False, "error": "user_identifier_type is required when user_identifier is provided"}
                    )

                # Check if the field (e.g., 'username' or 'email') matches the identifier
                if str(user_data.get(user_identifier_type)) != str(user_identifier):
                    continue

            # Filter by repository association if repository_id is provided
            if (
                repository_id
                and associated_user_ids is not None
                and uid not in associated_user_ids
            ):
                continue
            if role and user_data.get("role") != role:
                continue
            if user_data.get("status") != status:
                continue
            if (
                technical_expertise
                and user_data.get("technical_expertise") != technical_expertise
            ):
                continue

            results.append({**user_data, "user_id": uid})

        results.sort(
            key=lambda x: (
                x.get("last_name", ""),
                x.get("first_name", ""),
            )
        )

        return json.dumps(
            {
                "success": True,
                "count": len(results),
                "users": results,
                "repository_id": str(repository_id) if repository_id else None,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, object]:
        return {
            "type": "function",
            "function": {
                "name": "list_users",
                "description": "Find users and team members for projects and repositories. Perfect for identifying engineers, support staff, or people with specific technical skills. Filter by status, role, expertise, or link to a specific repository. Results are sorted alphabetically by name for easy browsing.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Filter by user status.",
                            "enum": ["active", "inactive"],
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Repository ID to validate and associate with user lookup",
                        },
                        "role": {
                            "type": "string",
                            "description": "Filter by user role.",
                            "enum": ["technical_engineer", "support_engineer"],
                        },
                        "technical_expertise": {
                            "type": "string",
                            "description": "Filter by technical expertise.",
                            "enum": ['db_admin', 'frontend_dev', 'backend_dev', 'security_specialist']
                        },
                        "user_identifier_type": {
                            "type": "string",
                            "description": "Specifies which unique attribute is being provided in the 'user_identifier' field. Mandatory when searching for a specific individual rather than a list.",
                            "enum": ["username", "email"]
                        },
                        "user_identifier": {
                            "type": "string",
                            "description": "The specific string value (the actual username or email address) used to retrieve a single user's details. Requires 'user_identifier_type' to be set"
                        }
                    },
                    "required": ["status"],
                },
            },
        }
