import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class SearchIssues(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: Optional[str] = None,
        issue_number: Optional[int] = None,
        status: Optional[str] = None,
        author_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
        priority: Optional[str] = None,
        issue_type: Optional[str] = None
    ) -> str:
        """
        Searches issues based on various filters.
        """
        issues = data.get("issues", {})
        results = []

        for issue in issues.values():
            match = True
            if repository_id and issue.get("repository_id") != repository_id:
                match = False
            if issue_number is not None and issue.get("issue_number") != issue_number:
                match = False
            if status and issue.get("status") != status:
                match = False
            if author_id and issue.get("author_id") != author_id:
                match = False
            if assignee_id and issue.get("assignee_id") != assignee_id:
                match = False
            if priority and issue.get("priority") != priority:
                match = False
            if issue_type and issue.get("issue_type") != issue_type:
                match = False
            
            if match:
                results.append(issue)

        return json.dumps(results)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "search_issues",
                "description": "Searches for issues matching the provided criteria.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Filter by repository ID."
                        },
                        "issue_number": {
                            "type": "integer",
                            "description": "Filter by issue number."
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by issue status. Allowed values: 'open', 'closed', 'in_progress'."
                        },
                        "author_id": {
                            "type": "string",
                            "description": "Filter by author ID."
                        },
                        "assignee_id": {
                            "type": "string",
                            "description": "Filter by assignee ID."
                        },
                        "priority": {
                            "type": "string",
                            "description": "Filter by priority. Allowed values: 'low', 'medium', 'high', 'critical'."
                        },
                        "issue_type": {
                            "type": "string",
                            "description": "Filter by issue type. Allowed values: 'bug', 'feature', 'documentation', 'question', 'enhancement'."
                        }
                    },
                    "required": []
                }
            }
        }