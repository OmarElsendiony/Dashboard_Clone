import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetIssues(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        search_field: Optional[str] = None,
        query: Optional[str] = None,
        limit: Optional[int] = 25,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if search_field is not None and not isinstance(search_field, str):
            return json.dumps({"success": False, "error": "Invalid Argument: 'search_field'"})

        if query is not None and not isinstance(query, str):
            return json.dumps({"success": False, "error": "Invalid Argument: 'query'"})

        if (search_field and not query) or (not search_field and query):
            return json.dumps({"success": False, "error": "Both 'search_field' and 'query' must be provided together, or both omitted to list all issues."})

        if limit is None:
            limit = 25

        if not isinstance(limit, int) or limit <= 0:
            return json.dumps({"success": False, "error": "Invalid Argument: 'limit'"})

        issues = data.get("issues", {})
        if not isinstance(issues, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'issues'"})

        matched = []

        if search_field and query:
            valid_search_fields = [
                "issue_id",
                "repository_id",
                "originating_ticket_id",
                "title",
                "description",
                "type",
                "status",
                "reproduction_verified",
                "reproduction_env",
                "created_at",
                "updated_at"
            ]

            if search_field not in valid_search_fields:
                return json.dumps({"success": False, "error": f"Invalid search_field: {search_field}, can only be {valid_search_fields}"})

            regex_fields = {"title", "description", "type", "status", "reproduction_env"}

            try:
                pattern = re.compile(query, re.IGNORECASE) if search_field in regex_fields else None
            except re.error:
                return json.dumps({"success": False, "error": "Invalid regex pattern in query"})

            for i in issues.values():
                if not isinstance(i, dict):
                    continue

                if search_field == "reproduction_verified":
                    target_value = str(bool(i.get("reproduction_verified"))).lower()
                    if target_value == str(query).lower():
                        matched.append(i)
                    continue

                raw_val = i.get(search_field)
                target_value = "" if raw_val is None else str(raw_val)

                if search_field in regex_fields:
                    if pattern.search(target_value):
                        matched.append(i)
                else:
                    if target_value == str(query):
                        matched.append(i)
        else:
            for i in issues.values():
                if isinstance(i, dict):
                    matched.append(i)

        matched.sort(key=lambda x: (
            "" if x.get("title") is None else str(x.get("title")).lower(),
            "" if x.get("issue_id") is None else str(x.get("issue_id"))
        ))

        matched = matched[:limit]

        formatted_issues = []
        for i in matched:
            formatted_issues.append({
                "issue_id": "" if i.get("issue_id") is None else str(i.get("issue_id")),
                "repository_id": "" if i.get("repository_id") is None else str(i.get("repository_id")),
                "originating_ticket_id": "" if i.get("originating_ticket_id") is None else str(i.get("originating_ticket_id")),
                "title": "" if i.get("title") is None else str(i.get("title")),
                "description": "" if i.get("description") is None else str(i.get("description")),
                "type": "" if i.get("type") is None else str(i.get("type")),
                "status": "" if i.get("status") is None else str(i.get("status")),
                "reproduction_verified": bool(i.get("reproduction_verified", False)),
                "reproduction_env": "" if i.get("reproduction_env") is None else str(i.get("reproduction_env")),
                "created_at": "" if i.get("created_at") is None else str(i.get("created_at")),
                "updated_at": "" if i.get("updated_at") is None else str(i.get("updated_at"))
            })

        return json.dumps({
            "success": True,
            "issues": formatted_issues,
            "returned_count": len(formatted_issues),
            "matched_count": len(matched),
            "message": "Issues retrieved successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_issues",
                "description": (
                    " Retrieves engineering issue records by querying a specific search field. Can also return a list of all issues if no search parameters are provided.\n"
                    " Purpose: Provides discovery and lookup of engineering issues, bugs, or feature requests based on their title, description, status, type, or related ticket ID to assist in ticket resolution and engineering escalations.\n"
                    " When to use: Use this tool when you need to find one or multiple issues using specific criteria, such as checking if an issue exists for a specific ticket, searching for keywords in issue descriptions, filtering by open or closed status, or retrieving a generic list of tracked engineering issues.\n"
                    " Returns: Returns a JSON string containing a success boolean, a list of matching issue dictionaries with their metadata, the returned count, and a success message text. "
                    "Default behavior: 'limit' defaults to 25 if not provided. If 'search_field' and 'query' are omitted, it lists all available issues up to the limit. "
                    "Regex search is supported and evaluated (case-insensitive) for the following search_fields: 'title', 'description', 'type', 'status', and 'reproduction_env'. "
                    "Exact string match is strictly required for the following search_fields: 'issue_id', 'repository_id', 'originating_ticket_id', 'reproduction_verified', 'created_at', and 'updated_at'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_field": {
                            "type": "string",
                            "enum": [
                                "issue_id",
                                "repository_id",
                                "originating_ticket_id",
                                "title",
                                "description",
                                "type",
                                "status",
                                "reproduction_verified",
                                "reproduction_env",
                                "created_at",
                                "updated_at"
                            ],
                            "description": "The specific field to search within. Optional; if omitted alongside query, the tool lists all issues."
                        },
                        "query": {
                            "type": "string",
                            "description": "The value or regex pattern to search for in the specified search field. Regex is supported for 'title', 'description', 'type', 'status', and 'reproduction_env'. Exact match is used for issue_id, repository_id, originating_ticket_id, reproduction_verified (e.g. 'true' or 'false'), created_at, and updated_at. Optional; if omitted alongside search_field, the tool lists all issues."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of issues to return. Default is 25."
                        }
                    },
                    "required": []
                }
            }
        }
