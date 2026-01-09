import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class AddNewIssue(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        title: str,
        author_id: str,
        issue_type: str,
        status: Optional[str] = None,
        description: Optional[str] = None,
        assignee_id: Optional[str] = None,
        priority: Optional[str] = None
    ) -> str:
        """
        Creates a new issue in a repository.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required to create an issue"})
        if not title:
            return json.dumps({"success": False, "error": "title is required to create an issue"})
        if not author_id:
            return json.dumps({"success": False, "error": "author_id is required to create an issue"})
        if not issue_type:
            return json.dumps({"success": False, "error": "issue_type is required to create an issue"})

        # Validate issue_type
        valid_issue_types = ["bug", "feature", "documentation", "question", "enhancement"]
        if issue_type not in valid_issue_types:
            return json.dumps({"success": False, "error": f"Invalid issue_type '{issue_type}'. Valid values: bug, feature, documentation, question, enhancement"})

        # Set default status if not provided
        if status is None:
            status = "open"

        # Validate status
        valid_statuses = ["open", "closed", "in_progress"]
        if status not in valid_statuses:
            return json.dumps({"success": False, "error": f"Invalid status '{status}'. Valid values: open, closed, in_progress"})

        # Validate priority if provided
        if priority is not None:
            valid_priorities = ["low", "medium", "high", "critical"]
            if priority not in valid_priorities:
                return json.dumps({"success": False, "error": f"Invalid priority '{priority}'. Valid values: low, medium, high, critical"})

        repositories = data.get("repositories", {})
        users = data.get("users", {})
        issues = data.get("issues", {})

        # Validate repository exists
        if str(repository_id) not in repositories:
            return json.dumps({"success": False, "error": f"Repository with id '{repository_id}' not found"})

        # Validate author exists
        if str(author_id) not in users:
            return json.dumps({"success": False, "error": f"User with id '{author_id}' not found"})

        # Validate assignee exists if provided
        if assignee_id is not None and str(assignee_id) not in users:
            return json.dumps({"success": False, "error": f"User with id '{assignee_id}' not found"})

        # Generate new issue_id
        if issues:
            max_id = max(int(k) for k in issues.keys())
            new_issue_id = str(max_id + 1)
        else:
            new_issue_id = "1"

        # Calculate issue_number (auto-increment per repository)
        repo_issue_numbers = [
            issue.get("issue_number", 0)
            for issue in issues.values()
            if str(issue.get("repository_id")) == str(repository_id)
        ]
        new_issue_number = max(repo_issue_numbers, default=0) + 1

        # Set closed_at if status is closed
        closed_at = "2026-01-01T23:59:00" if status == "closed" else None

        # Create issue record
        new_issue = {
            "issue_id": new_issue_id,
            "repository_id": repository_id,
            "issue_number": new_issue_number,
            "title": title,
            "description": description,
            "author_id": author_id,
            "assignee_id": assignee_id,
            "status": status,
            "priority": priority,
            "issue_type": issue_type,
            "closed_at": closed_at,
            "created_at": "2026-01-01T23:59:00",
            "updated_at": "2026-01-01T23:59:00"
        }

        issues[new_issue_id] = new_issue

        return json.dumps({"success": True, "result": new_issue})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_new_issue",
                "description": "Creates a new issue in a repository. Issues are used to track bugs, feature requests, documentation updates, questions, and enhancements. Each issue is assigned a unique issue number within the repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository where the issue will be created."
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the issue. Should be concise and descriptive."
                        },
                        "author_id": {
                            "type": "string",
                            "description": "The unique identifier of the user creating the issue."
                        },
                        "issue_type": {
                            "type": "string",
                            "description": "The type of issue. Valid values: bug, feature, documentation, question, enhancement."
                        },
                        "status": {
                            "type": "string",
                            "description": "The initial status of the issue. Valid values: open, closed, in_progress. Default: open."
                        },
                        "description": {
                            "type": "string",
                            "description": "A detailed description of the issue. Optional."
                        },
                        "assignee_id": {
                            "type": "string",
                            "description": "The unique identifier of the user assigned to work on this issue. Optional."
                        },
                        "priority": {
                            "type": "string",
                            "description": "The priority level of the issue. Valid values: low, medium, high, critical. Optional."
                        }
                    },
                    "required": ["repository_id", "title", "author_id", "issue_type"]
                }
            }
        }
