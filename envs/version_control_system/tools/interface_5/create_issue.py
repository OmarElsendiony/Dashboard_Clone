import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateIssue(Tool):
    """Tool for creating a new issue in a repository in the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        actor_id: str,
        title: str,
        description: Optional[str] = None,
        issue_type: str = "bug",
        priority: str = "medium",
    ) -> str:
        """
        Create a new issue in a repository.

        Args:
            data: The data dictionary containing all version control system data.
            repo_id: The ID of the repository to create the issue in (required).
            actor_id: The ID of the user creating the issue (required).
            title: The title of the issue (required).
            description: The description of the issue (optional).
            issue_type: The type of issue (bug/feature/documentation/question/enhancement, default: bug).
            priority: The priority of the issue (low/medium/high/critical, default: medium).

        Returns:
            str: A JSON-encoded string containing the success status and created issue data.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            """
            Generates a new unique ID for a record.

            Returns:
                str: The new unique ID as a string.
            """
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        def get_next_issue_number(issues: Dict[str, Any]) -> int:
            """
            Generates the next issue number.

            Returns:
                int: The next issue number.
            """
            if not issues:
                return 1
            return max(int(issue.get("issue_number", 0)) for issue in issues.values()) + 1

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        issues = data.get("issues", {})
        repositories = data.get("repositories", {})
        users = data.get("users", {})

        # Validate required fields
        if not repo_id:
            return json.dumps({"success": False, "error": "Missing required parameter: repo_id"})

        if not actor_id:
            return json.dumps({"success": False, "error": "Missing required parameter: actor_id"})

        if not title:
            return json.dumps({"success": False, "error": "Missing required parameter: title"})

        if not isinstance(title, str) or not title.strip():
            return json.dumps({"success": False, "error": "title must be a non-empty string"})

        # Validate repository exists
        repo_id = str(repo_id)
        if repo_id not in repositories:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repo_id}' not found"
            })

        repository = repositories[repo_id]

        # Check if repository is archived
        if repository.get("is_archived", False):
            return json.dumps({
                "success": False,
                "error": f"Cannot create issue in archived repository '{repo_id}'"
            })

        # Validate author exists
        actor_id = str(actor_id)
        if actor_id not in users:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{actor_id}' not found"
            })

        author = users[actor_id]

        # Check if author is active
        if author.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"User '{actor_id}' is not active"
            })

        # Validate issue_type
        allowed_issue_types = {"bug", "feature", "documentation", "question", "enhancement"}
        issue_type = issue_type.strip().lower() if isinstance(issue_type, str) else "bug"
        if issue_type not in allowed_issue_types:
            return json.dumps({
                "success": False,
                "error": f"issue_type must be one of: {', '.join(sorted(allowed_issue_types))}"
            })

        # Validate priority
        allowed_priorities = {"low", "medium", "high", "critical"}
        priority = priority.strip().lower() if isinstance(priority, str) else "medium"
        if priority not in allowed_priorities:
            return json.dumps({
                "success": False,
                "error": f"priority must be one of: {', '.join(sorted(allowed_priorities))}"
            })

        # Generate new issue ID and issue number
        new_issue_id = generate_id(issues)
        new_issue_number = get_next_issue_number(issues)

        # Set timestamp for created_at and updated_at
        timestamp = "2026-01-01T23:59:00"

        # Create new issue record
        new_issue = {
            "issue_id": new_issue_id,
            "repository_id": repo_id,
            "issue_number": int(new_issue_number),
            "title": title.strip(),
            "description": description.strip() if description else "",
            "author_id": actor_id,
            "assignee_id": None,
            "status": "open",
            "priority": priority,
            "issue_type": issue_type,
            "closed_at": None,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        # Add the new issue to the issues dictionary
        issues[new_issue_id] = new_issue

        return json.dumps({
            "success": True,
            "message": f"Issue '{title.strip()}' created successfully in repository '{repo_id}'",
            "issue_number": int(new_issue_number),
            "issue_data": new_issue
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the create_issue function."""
        return {
            "type": "function",
            "function": {
                "name": "create_issue",
                "description": "Create a new issue in a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository.",
                        },
                        "actor_id": {
                            "type": "string",
                            "description": "The ID of the user creating the issue.",
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the issue.",
                        },
                        "description": {
                            "type": "string",
                            "description": "The description of the issue.",
                        },
                        "issue_type": {
                            "type": "string",
                            "description": "Issue type; allowed values: bug, feature, documentation, question, enhancement. Defaults to bug.",
                        },
                        "priority": {
                            "type": "string",
                            "description": "Issue priority; allowed values: low, medium, high, critical. Defaults to medium.",
                        },
                    },
                    "required": ["repo_id", "actor_id", "title"],
                },
            },
        }
