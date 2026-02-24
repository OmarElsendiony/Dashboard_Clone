import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateIssue(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        title: str,
        originating_ticket_id: str,
        description: Optional[str] = None,
        issue_type: Optional[str] = "bug",
        reproduction_verified: Optional[bool] = False,
        reproduction_env: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        issues = data.get("issues", {})
        repositories = data.get("repositories", {})
        tickets = data.get("tickets", {})

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

        if not originating_ticket_id:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'originating_ticket_id' is required."
            })

        repository_id = str(repository_id).strip()
        title = str(title).strip()
        originating_ticket_id = str(originating_ticket_id).strip()
        description_str = str(description).strip() if description else ""
        issue_type_str = str(issue_type).strip().lower() if issue_type else "bug"
        reproduction_env_str = str(reproduction_env).strip() if reproduction_env else None

        if repository_id not in repositories:
            return json.dumps({
                "success": False,
                "error": f"Foreign Key Error: repository_id '{repository_id}' not found."
            })

        if originating_ticket_id not in tickets:
            return json.dumps({
                "success": False,
                "error": f"Foreign Key Error: originating_ticket_id '{originating_ticket_id}' not found in tickets table."
            })

        for issue in issues.values():
            if not isinstance(issue, dict):
                continue
            if (
                str(issue.get("repository_id")) == repository_id
                and str(issue.get("title", "")).strip().lower() == title.lower()
                and str(issue.get("status", "")).lower() != "closed"
            ):
                return json.dumps({
                    "success": True,
                    "issue": issue,
                    "message": "Issue already exists. Returning existing record (idempotent)."
                })

        max_id = 0
        for k in issues.keys():
            try:
                num = int(str(k))
                if num > max_id:
                    max_id = num
            except ValueError:
                continue

        new_issue_id = str(max_id + 1)
        timestamp = "2026-02-02 23:59:00"

        new_issue = {
            "issue_id": new_issue_id,
            "repository_id": repository_id,
            "originating_ticket_id": originating_ticket_id,
            "title": title,
            "description": description_str,
            "type": issue_type_str,
            "status": "Open",
            "reproduction_verified": bool(reproduction_verified),
            "reproduction_env": reproduction_env_str,
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
                    "Creates a new formal engineering issue within a specified repository, strictly mapping to the database schema.\n"
                    " Purpose: Designed to escalate a confirmed defect from support to the engineering team. It links the issue directly to the originating support ticket to trigger the engineering workflow.\n"
                    " When to use: Use this tool to file an issue after gathering valid reproduction steps and confirming a bug. The title must follow standard formatting.\n"
                    " Returns: A JSON string containing a success boolean, the newly created issue dictionary object (or the existing one if an open issue with the same title exists in the target repository), and a success message. Fails if the repository or originating ticket does not exist."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the target repository where the issue will be tracked."
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the issue. Should ideally follow format: [Component Name] [Error Code/Exception]."
                        },
                        "originating_ticket_id": {
                            "type": "string",
                            "description": "The unique identifier of the support ticket that generated this issue."
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed reproduction steps, evidence, and context about the issue. Optional but recommended."
                        },
                        "issue_type": {
                            "type": "string",
                            "description": "The category of the issue (e.g., 'bug', 'configuration', 'feature'). Defaults to 'bug'."
                        },
                        "reproduction_verified": {
                            "type": "boolean",
                            "description": "Flag indicating if the bug reproduction was successfully verified by support. Defaults to False."
                        },
                        "reproduction_env": {
                            "type": "string",
                            "description": "The environment where the issue was reproduced (e.g., 'prod', 'staging'). Optional."
                        }
                    },
                    "required": ["repository_id", "title", "originating_ticket_id"]
                }
            }
        }
