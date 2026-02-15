import json
from typing import Dict, Optional
from tau_bench.envs.tool import Tool


class SearchIssues(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, object],
        repository_id: Optional[str] = None,
        title: Optional[str] = None,
        description_contains: Optional[str] = None,
        status: Optional[str] = None,
        type: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for issues"}
            )

        if not any([repository_id, title, description_contains, status, type]):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one search parameter must be provided",
                }
            )

        issues = data.get("issues", {})
        results = []

        if status:
            valid_statuses = ["Open", "In_Progress", "Resolved"]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                    }
                )

        if type:
            valid_types = ["feature", "incident", "bug", "configuration"]
            if type not in valid_types:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid type '{type}'. Must be one of: {', '.join(valid_types)}",
                    }
                )

        for issue_id_key, issue_data in issues.items():
            if repository_id and str(issue_data.get("repository_id")) != str(
                repository_id
            ):
                continue
            if status and issue_data.get("status") != status:
                continue
            if type and issue_data.get("type") != type:
                continue

            if title:
                issue_title = issue_data.get("title", "").lower()
                search_title = title.lower()
                if search_title not in issue_title:
                    continue

            if description_contains:
                issue_description = issue_data.get("description", "").lower()
                search_description = description_contains.lower()
                if search_description not in issue_description:
                    continue

            results.append({**issue_data, "issue_id": issue_id_key})

        results.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

        return json.dumps(
            {
                "success": True,
                "count": len(results),
                "issues": results,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, object]:
        return {
            "type": "function",
            "function": {
                "name": "search_issues",
                "description": "Find issues that match what you're looking for across multiple criteria. Perfect for checking if similar issues already exist before creating new ones or when linking tickets to existing problems. Searches through titles and descriptions with smart matching - just type part of what you're looking for and it'll find it.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Filter by repository ID",
                        },
                        "title": {
                            "type": "string",
                            "description": "Search for issues by title (supports partial matching, case-insensitive)",
                        },
                        "description_contains": {
                            "type": "string",
                            "description": "Search for issues by description content (supports partial matching, case-insensitive)",
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by issue status.",
                            "enum": ["Open", "In_Progress", "Resolved"],
                        },
                        "type": {
                            "type": "string",
                            "description": "Filter by issue type.",
                            "enum": ["feature", "incident", "bug", "configuration"],
                        },
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["repository_id"]},
                        {"required": ["title"]},
                        {"required": ["description_contains"]},
                        {"required": ["status"]},
                        {"required": ["type"]},
                    ],
                },
            },
        }
