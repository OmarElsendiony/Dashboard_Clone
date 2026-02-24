import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetRepositories(Tool):
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
            return json.dumps({
                "success": False,
                "error": "Both 'search_field' and 'query' must be provided together, or both omitted to list all repositories."
            })

        try:
            limit_val = int(limit) if limit is not None else 25
            if limit_val <= 0:
                limit_val = 25
        except (ValueError, TypeError):
            limit_val = 25

        repositories = data.get("repositories", {})
        if not isinstance(repositories, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'repositories' table missing or malformed."})

        matched = []

        if search_field and query:
            valid_search_fields = [
                "repository_id",
                "repository_name",
                "description",
                "default_branch",
                "created_at",
                "updated_at"
            ]

            if search_field not in valid_search_fields:
                return json.dumps({"success": False, "error": f"Invalid search_field: {search_field}. Must be one of {valid_search_fields}"})

            regex_fields = {"repository_name", "description", "default_branch"}

            try:
                pattern = re.compile(query, re.IGNORECASE) if search_field in regex_fields else None
            except re.error:
                return json.dumps({"success": False, "error": "Invalid regex pattern in query."})

            for repo in repositories.values():
                if not isinstance(repo, dict):
                    continue

                raw_val = repo.get(search_field)
                target_value = "" if raw_val is None else str(raw_val)

                if search_field in regex_fields:
                    if pattern.search(target_value):
                        matched.append(repo)
                else:
                    if target_value == str(query):
                        matched.append(repo)
        else:
            for repo in repositories.values():
                if isinstance(repo, dict):
                    matched.append(repo)

        matched.sort(key=lambda x: (
            str(x.get("repository_name", "")).lower(),
            str(x.get("repository_id", ""))
        ))

        matched = matched[:limit_val]

        formatted_repos = []
        for r in matched:
            formatted_repos.append({
                "repository_id": str(r.get("repository_id", "")),
                "repository_name": str(r.get("repository_name", "")),
                "description": str(r.get("description", "")),
                "default_branch": str(r.get("default_branch", "")),
                "created_at": str(r.get("created_at", "")),
                "updated_at": str(r.get("updated_at", ""))
            })

        return json.dumps({
            "success": True,
            "repositories": formatted_repos,
            "returned_count": len(formatted_repos),
            "matched_count": len(matched),
            "message": "Repositories retrieved successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_repositories",
                "description": (
                    "Retrieves engineering repository records from the central codebase registry by querying specific metadata fields. It can also list all available repositories if search parameters are omitted.\n"
                    " Purpose: This is the primary Service Discovery tool. It allows mapping high-level service names (like 'Logistics Shipping Service') to technical 'repository_id' values, which are required as inputs for other engineering tools such as 'create_issue', 'create_branch', and 'create_pull_request'.\n"
                    " When to use: Use this tool whenever you need to find a specific repository by name or identifier, verify which service handles a particular module, or check the default development branch (e.g., 'main' vs 'master') for a project.\n"
                    " Returns: Returns a JSON string containing a success flag, a list of repository metadata dictionaries, and record counts. "
                    "Default behavior: 'limit' defaults to 25. If 'search_field' and 'query' are omitted, it returns all services (repositories) up to the limit. "
                    "Search behavior: Case-insensitive regex searching is supported for 'repository_name', 'description', and 'default_branch'. "
                    "Strict exact string matching is required for 'repository_id', 'created_at', and 'updated_at'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_field": {
                            "type": "string",
                            "enum": [
                                "repository_id",
                                "repository_name",
                                "description",
                                "default_branch",
                                "created_at",
                                "updated_at"
                            ],
                            "description": "The specific field or column in the repositories table to search within."
                        },
                        "query": {
                            "type": "string",
                            "description": "The exact value or regex pattern to search for. Regex is evaluated case-insensitively for name, description, and branch fields."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "The maximum number of repository records to return. Defaults to 25."
                        }
                    },
                    "required": []
                }
            }
        }
