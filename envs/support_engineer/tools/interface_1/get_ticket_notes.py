import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetTicketNotes(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        entity: Optional[str] = "note",
        search_field: Optional[str] = None,
        query: Optional[str] = None,
        limit: Optional[int] = 25,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if entity is None:
            entity = "note"

        if entity not in ["note", "tag"]:
            return json.dumps({"success": False, "error": "Invalid Argument: 'entity' must be strictly 'note' or 'tag'."})

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

        if entity == "note":
            db_table = data.get("ticket_notes", {})
            valid_search_fields = ["note_id", "ticket_id", "author_id", "title", "body", "file_path", "is_internal", "sanitization_status", "created_at"]
            regex_fields = {"title", "body", "file_path", "sanitization_status"}
        else:
            db_table = data.get("tags", {})
            valid_search_fields = ["tag_id", "tag_name", "tag_type"]
            regex_fields = {"tag_name", "tag_type"}

        if not isinstance(db_table, dict):
            return json.dumps({"success": False, "error": f"Invalid data format: '{entity}s' table missing or malformed."})

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

        if entity == "note":
            matched.sort(key=lambda x: (
                str(x.get("ticket_id", "")),
                str(x.get("note_id", ""))
            ))
        else:
            matched.sort(key=lambda x: (
                str(x.get("tag_name", "")).lower(),
                str(x.get("tag_id", ""))
            ))

        matched = matched[:limit]
        formatted_results = []

        if entity == "note":
            for n in matched:
                formatted_results.append({
                    "note_id": str(n.get("note_id", "")),
                    "ticket_id": str(n.get("ticket_id", "")),
                    "author_id": str(n.get("author_id", "")),
                    "title": str(n.get("title", "")) if n.get("title") is not None else "",
                    "body": str(n.get("body", "")),
                    "file_path": str(n.get("file_path", "")) if n.get("file_path") is not None else "",
                    "is_internal": bool(n.get("is_internal", True)),
                    "sanitization_status": str(n.get("sanitization_status", "")),
                    "created_at": str(n.get("created_at", ""))
                })
        else:
            for t in matched:
                formatted_results.append({
                    "tag_id": str(t.get("tag_id", "")),
                    "tag_name": str(t.get("tag_name", "")),
                    "tag_type": str(t.get("tag_type", ""))
                })

        return json.dumps({
            "success": True,
            "entity_type": entity,
            "results": formatted_results,
            "returned_count": len(formatted_results),
            "matched_count": len(matched),
            "message": f"{entity.capitalize()}s retrieved successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_ticket_notes",
                "description": (
                    " A combined discovery tool that retrieves either internal ticket notes or system tags by querying a specific search field."
                    " Purpose: Facilitates the discovery of internal ticket notes (for finding attachment file paths prior to sanitization) and tags (for discovering integer tag IDs prior to updating a ticket)."
                    " When to use: Use this tool to look up internal notes (e.g., searching by 'file_path' or 'ticket_id') or classification tags (e.g., searching by 'tag_name' like 'Duplicate'). The 'entity' parameter is optional and defaults to 'note'."
                    " Returns: A JSON string containing a success boolean, the matching list of dictionaries under 'results', and record counts."
                    "Search behavior and Fields:\n"
                    " - For entity='note' (default): Valid fields are note_id, ticket_id, author_id, title, body, file_path, is_internal, sanitization_status, created_at. Regex is supported (case-insensitive) for title, body, file_path, and sanitization_status."
                    " - For entity='tag': Valid fields are tag_id, tag_name, tag_type. Regex is supported (case-insensitive) for tag_name and tag_type."
                    "Exact matches (case-insensitive) are required for IDs and timestamp fields. An error is strictly returned if a field exclusive to one entity is queried against the other."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entity": {
                            "type": "string",
                            "enum": ["note", "tag"],
                            "description": "Optional. The type of entity to search for: 'note' (for ticket_notes) or 'tag'. Defaults to 'note'."
                        },
                        "search_field": {
                            "type": "string",
                            "enum": [
                                "note_id",
                                "ticket_id",
                                "author_id",
                                "title",
                                "body",
                                "file_path",
                                "is_internal",
                                "sanitization_status",
                                "created_at",
                                "tag_id",
                                "tag_name",
                                "tag_type"
                            ],
                            "description": "Optional. The specific field to search within based on the entity type. Passing a tag field for a note entity (or vice versa) will result in an explicit error. If omitted alongside query, all records are returned."
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
