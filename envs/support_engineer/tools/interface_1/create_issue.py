import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateIssue(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: int,
        title: str,
        creator_id: int,
        body: Optional[str] = None,
        priority: Optional[str] = "medium",
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        issues = data.get("issues", {})
        repositories = data.get("repositories", {})
        users = data.get("users", {})

        if not repository_id:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'repository_id' is required."
            })

        if not title:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'title' is required."
            })

        if not creator_id:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'creator_id' is required."
            })

        if str(repository_id) not in repositories:
            return json.dumps({
                "success": False,
                "error": f"Foreign Key Error: repository_id '{repository_id}' not found."
            })

        if str(creator_id) not in users:
            return json.dumps({
                "success": False,
                "error": f"Authorization Error: User ID '{creator_id}' not found."
            })

        valid_priorities = ["low", "medium", "high", "urgent"]
        final_priority = priority.lower() if priority else "medium"

        if final_priority not in valid_priorities:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: priority must be one of {valid_priorities}."
            })

        reproduction_verified = data.get("reproduction_verified")
        if reproduction_verified is not None and reproduction_verified is False:
            return json.dumps({
                "success": False,
                "error": "SOP Violation: Issue cannot be created until reproduction is verified."
            })

        for issue in issues.values():
            if (
                int(issue.get("repository_id")) == int(repository_id)
                and issue.get("title", "").strip().lower() == title.strip().lower()
                and issue.get("status", "").lower() != "closed"
            ):
                return json.dumps({
                    "success": True,
                    "issue": issue,
                    "message": "Issue already exists. Returning existing record (idempotent)."
                })

        if issues:
            new_issue_id = str(max(int(k) for k in issues.keys()) + 1)
        else:
            new_issue_id = "1"

        timestamp = "2026-02-02 23:59:00"

        new_issue = {
            "issue_id": int(new_issue_id),
            "repository_id": int(repository_id),
            "title": title,
            "body": body or "",
            "priority": final_priority,
            "creator_id": int(creator_id),
            "status": "open",
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        issues[new_issue_id] = new_issue

        return json.dumps({
            "success": True,
            "issue": new_issue,
            "message": f"Issue '{title}' created successfully in repository {repository_id}."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_issue",
                "description": (
                    "Escalates a confirmed defect to the engineering team by creating a formal issue record. "
                    "This action triggers the engineering workflow and must only be performed after valid reproduction artifacts "
                    "(procedural steps and technical evidence) have been confirmed in the support ticket."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "integer",
                            "description": "The unique ID of the repository where the issue will be tracked."
                        },
                        "title": {
                            "type": "string",
                            "description": "Must follow format: [Component Name] [Error Code/Exception]."
                        },
                        "body": {
                            "type": "string",
                            "description": "Detailed reproduction steps and evidence (optional)."
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Severity level (optional, default = medium)."
                        },
                        "creator_id": {
                            "type": "integer",
                            "description": "Support Engineer performing escalation."
                        },
                    },
                    "required": ["repository_id", "title", "creator_id"]
                },
            },
        }
