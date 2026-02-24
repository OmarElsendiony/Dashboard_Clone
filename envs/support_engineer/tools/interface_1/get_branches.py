import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetBranches(Tool):
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
                "error": "Both 'search_field' and 'query' must be provided together, or both omitted to list all branches."
            })

        try:
            limit_val = int(limit) if limit is not None else 25
            if limit_val <= 0:
                limit_val = 25
        except (ValueError, TypeError):
            limit_val = 25

        branches = data.get("branches", {})
        if not isinstance(branches, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'branches' table missing or malformed."})

        matched = []

        if search_field and query:
            valid_search_fields = [
                "branch_id",
                "repository_id",
                "branch_name",
                "source_branch_name",
                "commit_sha",
                "branch_type",
                "linked_ticket_id",
                "issue_id",
                "created_by",
                "status",
                "created_at",
                "updated_at"
            ]

            if search_field not in valid_search_fields:
                return json.dumps({"success": False, "error": f"Invalid search_field: {search_field}. Must be one of {valid_search_fields}"})

            regex_fields = {"branch_name", "source_branch_name", "branch_type", "status"}

            try:
                pattern = re.compile(query, re.IGNORECASE) if search_field in regex_fields else None
            except re.error:
                return json.dumps({"success": False, "error": "Invalid regex pattern in query."})

            for branch in branches.values():
                if not isinstance(branch, dict):
                    continue

                raw_val = branch.get(search_field)
                target_value = "" if raw_val is None else str(raw_val)

                if search_field in regex_fields:
                    if pattern.search(target_value):
                        matched.append(branch)
                else:
                    if target_value == str(query):
                        matched.append(branch)
        else:
            for branch in branches.values():
                if isinstance(branch, dict):
                        matched.append(branch)

        matched.sort(key=lambda x: (
            str(x.get("branch_name", "")).lower(),
            str(x.get("branch_id", ""))
        ))

        matched = matched[:limit_val]

        formatted_branches = []
        for b in matched:
            formatted_branches.append({
                "branch_id": str(b.get("branch_id", "")),
                "repository_id": str(b.get("repository_id", "")),
                "branch_name": str(b.get("branch_name", "")),
                "source_branch_name": str(b.get("source_branch_name", "")) if b.get("source_branch_name") is not None else "",
                "commit_sha": str(b.get("commit_sha", "")),
                "branch_type": str(b.get("branch_type", "")) if b.get("branch_type") is not None else "",
                "linked_ticket_id": str(b.get("linked_ticket_id", "")) if b.get("linked_ticket_id") is not None else "",
                "issue_id": str(b.get("issue_id", "")) if b.get("issue_id") is not None else "",
                "created_by": str(b.get("created_by", "")),
                "status": str(b.get("status", "")),
                "created_at": str(b.get("created_at", "")),
                "updated_at": str(b.get("updated_at", ""))
            })

        return json.dumps({
            "success": True,
            "branches": formatted_branches,
            "returned_count": len(formatted_branches),
            "matched_count": len(matched),
            "message": "Branches retrieved successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_branches",
                "description": (
                    "Retrieves version control branch records from the database by querying specific metadata fields. It can list all available branches if search parameters are omitted.\n"
                    " Purpose: Facilitates the discovery of existing codebase branches prior to initiating a Pull Request. It bridges the gap between the 'Standardize Code Branches' and 'Validate and Submit PRs' SOPs by allowing an agent to fetch the exact branch mapped to a specific ticket.\n"
                    " When to use: Use this tool to look up a branch by its 'linked_ticket_id', 'repository_id', or 'branch_name' before attempting to create or merge a pull request.\n"
                    " Returns: Returns a JSON string containing a success flag, a list of branch metadata dictionaries, and record counts. "
                    "Default behavior: 'limit' defaults to 25. If 'search_field' and 'query' are omitted, it returns all branches up to the limit. "
                    "Search behavior: Case-insensitive regex searching is supported for 'branch_name', 'source_branch_name', 'branch_type', and 'status'. "
                    "Strict exact string matching is required for 'branch_id', 'repository_id', 'commit_sha', 'linked_ticket_id', 'issue_id', 'created_by', 'created_at', and 'updated_at'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_field": {
                            "type": "string",
                            "enum": [
                                "branch_id",
                                "repository_id",
                                "branch_name",
                                "source_branch_name",
                                "commit_sha",
                                "branch_type",
                                "linked_ticket_id",
                                "issue_id",
                                "created_by",
                                "status",
                                "created_at",
                                "updated_at"
                            ],
                            "description": "The specific field in the branches table to search within."
                        },
                        "query": {
                            "type": "string",
                            "description": "The exact value or regex pattern to search for. Regex is evaluated case-insensitively for branch names, type, and status."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "The maximum number of branch records to return. Defaults to 25."
                        }
                    },
                    "required": []
                }
            }
        }
