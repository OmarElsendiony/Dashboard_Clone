import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetBranches(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        entity: Optional[str] = "branch",
        search_field: Optional[str] = None,
        query: Optional[str] = None,
        limit: Optional[int] = 25,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if entity is None:
            entity = "branch"

        if entity not in ["branch", "pull_request"]:
            return json.dumps({"success": False, "error": "Invalid Argument: 'entity' must be strictly 'branch' or 'pull_request'."})

        if search_field is not None and not isinstance(search_field, str):
            return json.dumps({"success": False, "error": "Invalid Argument: 'search_field'"})

        if query is not None and not isinstance(query, str):
            return json.dumps({"success": False, "error": "Invalid Argument: 'query'"})

        if (search_field and not query) or (not search_field and query):
            return json.dumps({"success": False, "error": "Both 'search_field' and 'query' must be provided together, or both omitted to list all."})

        if limit is not None:
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                return json.dumps({"success": False, "error": "Invalid Argument: 'limit' must be an integer."})
            if limit <= 0:
                return json.dumps({"success": False, "error": "Invalid Argument: 'limit' must be positive."})
        else:
            limit = 25

        matched = []

        if entity == "branch":
            db_table = data.get("branches", {})
            valid_search_fields = [
                "branch_id", "repository_id", "branch_name", "source_branch_name",
                "commit_sha", "branch_type", "linked_ticket_id", "issue_id",
                "created_by", "status", "created_at", "updated_at"
            ]
            regex_fields = {"branch_name", "source_branch_name", "branch_type", "status"}
        else:
            db_table = data.get("pull_requests", {})
            valid_search_fields = [
                "pull_request_id", "repository_id", "pull_request_number", "title",
                "description", "source_branch_name", "target_branch_name", "author_id",
                "status", "linked_ticket_id", "gate_traceability", "gate_test_coverage",
                "gate_ci_status", "is_emergency_fix", "assigned_team_lead", "merged_by",
                "merged_at", "closed_at", "created_at", "updated_at"
            ]
            regex_fields = {"title", "description", "source_branch_name", "target_branch_name"}

        if not isinstance(db_table, dict):
            return json.dumps({"success": False, "error": f"Invalid data format: '{entity}' table missing or malformed."})

        if search_field and query:
            if search_field not in valid_search_fields:
                return json.dumps({
                    "success": False,
                    "error": "Field Mismatch Error",
                    "message": f"Invalid search_field '{search_field}' for entity '{entity}'. Valid options for '{entity}' are: {valid_search_fields}."
                })

            try:
                pattern = re.compile(query, re.IGNORECASE) if search_field in regex_fields else None
            except re.error:
                return json.dumps({"success": False, "error": "Invalid regex pattern in query."})

            for item in db_table.values():
                if not isinstance(item, dict):
                    continue

                raw_val = item.get(search_field)
                target_value = "" if raw_val is None else str(raw_val)

                if search_field in regex_fields:
                    if pattern.search(target_value):
                        matched.append(item)
                else:
                    if target_value.lower() == str(query).lower():
                        matched.append(item)
        else:
            for item in db_table.values():
                if isinstance(item, dict):
                    matched.append(item)

        if entity == "branch":
            matched.sort(key=lambda x: (
                str(x.get("branch_name", "")).lower(),
                str(x.get("branch_id", ""))
            ))
        else:
            matched.sort(key=lambda x: (
                str(x.get("repository_id", "")),
                str(x.get("pull_request_id", ""))
            ))

        matched = matched[:limit]
        formatted_results = []

        if entity == "branch":
            for b in matched:
                formatted_results.append({
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
        else:
            for pr in matched:
                formatted_results.append({
                    "pull_request_id": str(pr.get("pull_request_id", "")),
                    "repository_id": str(pr.get("repository_id", "")),
                    "pull_request_number": int(pr.get("pull_request_number", 0)) if pr.get("pull_request_number") is not None else 0,
                    "title": str(pr.get("title", "")),
                    "description": str(pr.get("description", "")),
                    "source_branch_name": str(pr.get("source_branch_name", "")),
                    "target_branch_name": str(pr.get("target_branch_name", "")),
                    "author_id": str(pr.get("author_id", "")),
                    "status": str(pr.get("status", "")),
                    "linked_ticket_id": str(pr.get("linked_ticket_id", "")),
                    "gate_traceability": bool(pr.get("gate_traceability", False)),
                    "gate_test_coverage": bool(pr.get("gate_test_coverage", False)),
                    "gate_ci_status": str(pr.get("gate_ci_status", "")),
                    "is_emergency_fix": bool(pr.get("is_emergency_fix", False)),
                    "assigned_team_lead": str(pr.get("assigned_team_lead", "")) if pr.get("assigned_team_lead") is not None else None,
                    "merged_by": str(pr.get("merged_by", "")) if pr.get("merged_by") is not None else None,
                    "merged_at": str(pr.get("merged_at", "")) if pr.get("merged_at") is not None else None,
                    "closed_at": str(pr.get("closed_at", "")) if pr.get("closed_at") is not None else None,
                    "created_at": str(pr.get("created_at", "")),
                    "updated_at": str(pr.get("updated_at", ""))
                })

        return json.dumps({
            "success": True,
            "entity_type": entity,
            "results": formatted_results,
            "returned_count": len(formatted_results),
            "matched_count": len(matched),
            "message": f"{entity.replace('_', ' ').capitalize()}s retrieved successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_branches",
                "description": (
                    "A combined discovery tool that retrieves either version control branch records or pull request records from the database.\n"
                    " Purpose: Facilitates the discovery of existing codebase branches prior to initiating a Pull Request, or auditing open pull requests linked to specific tickets. It bridges the gap between the 'Standardize Code Branches' and 'Validate and Submit PRs' SOPs.\n"
                    " When to use: Use this tool to look up a branch or PR by passing the corresponding 'entity'. The 'entity' parameter defaults to 'branch' if omitted.\n"
                    " Returns: Returns a JSON string containing a success flag, the matching list of dictionaries under 'results', and record counts. An explicit error is returned if a field exclusive to one entity is queried against the other.\n"
                    "Search behavior and Fields:"
                    " - For entity='branch' (default): Valid fields are branch_id, repository_id, branch_name, source_branch_name, commit_sha, branch_type, linked_ticket_id, issue_id, created_by, status, created_at, updated_at. Regex is supported (case-insensitive) for branch_name, source_branch_name, branch_type, and status.\n"
                    " - For entity='pull_request': Valid fields are pull_request_id, repository_id, pull_request_number, title, description, source_branch_name, target_branch_name, author_id, status, linked_ticket_id, gate_traceability, gate_test_coverage, gate_ci_status, is_emergency_fix, assigned_team_lead, merged_by, merged_at, closed_at, created_at, updated_at. Regex is supported (case-insensitive) for title, description, source_branch_name, and target_branch_name.\n"
                    "Exact matching (case-insensitive) is required for IDs, numbers, booleans, and timestamp fields. Default limit is 25."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entity": {
                            "type": "string",
                            "enum": ["branch", "pull_request"],
                            "description": "Optional. The type of entity to search for. Must be 'branch' or 'pull_request'. Defaults to 'branch'."
                        },
                        "search_field": {
                            "type": "string",
                            "description": "Optional. The specific field to search within based on the entity type. Passing a pull_request field for a branch entity (or vice versa) will result in an explicit error. If omitted alongside query, all records are returned."
                        },
                        "query": {
                            "type": "string",
                            "description": "Optional. The value or regex pattern to search for in the specified field."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Optional. Maximum number of records to return. Default is 25."
                        }
                    },
                    "required": []
                }
            }
        }
