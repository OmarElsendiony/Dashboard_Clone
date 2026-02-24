import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetComments(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        identifier: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: Optional[int] = 25,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if identifier is not None and not isinstance(identifier, str):
            return json.dumps({"success": False, "error": "Invalid Argument: 'identifier'"})

        if search_query is not None and not isinstance(search_query, str):
            return json.dumps({"success": False, "error": "Invalid Argument: 'search_query'"})

        if (identifier and not search_query) or (not identifier and search_query):
            return json.dumps({"success": False, "error": "Both 'identifier' and 'search_query' must be provided together, or both omitted to list all comments."})

        if limit is not None:
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                return json.dumps({"success": False, "error": "Invalid Argument: 'limit' must be an integer."})
            if limit <= 0:
                return json.dumps({"success": False, "error": "Invalid Argument: 'limit' must be positive."})
        else:
            limit = 25

        ticket_comments = data.get("ticket_comments", {})
        if not isinstance(ticket_comments, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'ticket_comments'"})

        matched = []

        if identifier and search_query:
            valid_identifiers = [
                "comment_id",
                "ticket_id",
                "sender_id",
                "message",
                "is_public",
                "created_at",
                "updated_at"
            ]

            if identifier not in valid_identifiers:
                return json.dumps({"success": False, "error": f"Invalid identifier: {identifier}, can only be {valid_identifiers}"})

            regex_fields = {"message"}

            try:
                pattern = re.compile(search_query, re.IGNORECASE) if identifier in regex_fields else None
            except re.error:
                return json.dumps({"success": False, "error": "Invalid regex pattern in search_query"})

            for c in ticket_comments.values():
                if not isinstance(c, dict):
                    continue

                if identifier == "is_public":
                    target_value = str(bool(c.get("is_public"))).lower()
                    if target_value == str(search_query).lower():
                        matched.append(c)
                    continue

                target_value = str(c.get(identifier, ""))

                if identifier in regex_fields:
                    if pattern.search(target_value):
                        matched.append(c)
                else:
                    if target_value == str(search_query):
                        matched.append(c)
        else:
            for c in ticket_comments.values():
                if isinstance(c, dict):
                    matched.append(c)

        def get_sort_keys(c_dict):
            created_at = str(c_dict.get("created_at", ""))
            comment_id = str(c_dict.get("comment_id", ""))
            try:
                numeric_id = int(comment_id)
            except Exception:
                numeric_id = None
            return (
                created_at,
                0 if numeric_id is not None else 1,
                numeric_id if numeric_id is not None else 0,
                comment_id
            )

        matched.sort(key=get_sort_keys)
        matched = matched[:limit]

        comments = []
        for c in matched:
            comments.append({
                "comment_id": str(c.get("comment_id", "")),
                "ticket_id": str(c.get("ticket_id", "")),
                "sender_id": str(c.get("sender_id", "")),
                "message": str(c.get("message", "")),
                "is_public": bool(c.get("is_public", False)),
                "created_at": str(c.get("created_at", "")),
                "updated_at": str(c.get("updated_at", ""))
            })

        return json.dumps({
            "success": True,
            "comments": comments,
            "returned_count": len(comments),
            "matched_count": len(matched),
            "message": "Ticket comments retrieved successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_comments",
                "description": (
                    " Retrieves ticket comments by querying a specific identifier field. Can also return a list of all comments chronologically if no search parameters are provided.\n"
                    " Purpose: Provides visibility into customer and agent communication on a ticket, allowing filtering by exact matches or regex patterns.\n"
                    " When to use: Use this tool when auditing conversations, searching for specific troubleshooting steps, or retrieving comments associated with a specific ticket or sender.\n"
                    " Returns: Returns a JSON string containing a success boolean, a list of matching comment dictionaries with their metadata, the returned count, and a success message text. "
                    "Default behavior: 'limit' defaults to 25 if not provided. If 'identifier' and 'search_query' are omitted, it lists all available comments up to the limit. "
                    "Regex search is supported and evaluated (case-insensitive) for the following identifier: 'message'. "
                    "Exact string match is strictly required for the following identifiers: 'comment_id', 'ticket_id', 'sender_id', 'is_public', 'created_at', and 'updated_at'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "identifier": {
                            "type": "string",
                            "enum": [
                                "comment_id",
                                "ticket_id",
                                "sender_id",
                                "message",
                                "is_public",
                                "created_at",
                                "updated_at"
                            ],
                            "description": "The specific field or identifier to search within. Optional; if omitted alongside search_query, the tool lists all comments."
                        },
                        "search_query": {
                            "type": "string",
                            "description": "The value or regex pattern to search for in the specified identifier field. Regex is supported for the 'message' field. Exact match is used for comment_id, ticket_id, sender_id, is_public, created_at, and updated_at. Optional; if omitted alongside identifier, the tool lists all comments."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of comments to return. Default is 25."
                        }
                    },
                "required" : []
                }
            }
        }
