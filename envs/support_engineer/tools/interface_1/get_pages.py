import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetPages(Tool):
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
            return json.dumps({"success": False, "error": "Both 'search_field' and 'query' must be provided together, or both omitted to list all pages."})

        if limit is None:
            limit = 25

        if not isinstance(limit, int) or limit <= 0:
            return json.dumps({"success": False, "error": "Invalid Argument: 'limit'"})

        documents = data.get("documents", {})
        if not isinstance(documents, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'documents'"})

        matched = []

        field_map = {
            "page_id": "document_id",
            "page_name": "doc_name",
            "title": "title",
            "description": "description",
            "related_ticket_id": "related_ticket_id",
            "space_key": "space_key",
            "status": "status",
            "created_at": "created_at",
            "updated_at": "updated_at"
        }

        if search_field and query:
            valid_search_fields = list(field_map.keys())

            if search_field not in valid_search_fields:
                return json.dumps({"success": False, "error": f"Invalid search_field: {search_field}, can only be {valid_search_fields}"})

            regex_fields = {"page_name", "title", "description", "status"}

            try:
                pattern = re.compile(query, re.IGNORECASE) if search_field in regex_fields else None
            except re.error:
                return json.dumps({"success": False, "error": "Invalid regex pattern in query"})

            internal_key = field_map[search_field]

            for doc in documents.values():
                if not isinstance(doc, dict):
                    continue

                raw_val = doc.get(internal_key)
                target_value = "" if raw_val is None else str(raw_val)

                if search_field in regex_fields:
                    if pattern.search(target_value):
                        matched.append(doc)
                else:
                    if target_value == str(query):
                        matched.append(doc)
        else:
            for doc in documents.values():
                if isinstance(doc, dict):
                    matched.append(doc)

        matched.sort(key=lambda x: (
            "" if x.get("title") is None else str(x.get("title")).lower(),
            "" if x.get("document_id") is None else str(x.get("document_id"))
        ))

        matched = matched[:limit]

        pages = []
        for d in matched:
            pages.append({
                "page_id": "" if d.get("document_id") is None else str(d.get("document_id")),
                "page_name": "" if d.get("doc_name") is None else str(d.get("doc_name")),
                "title": "" if d.get("title") is None else str(d.get("title")),
                "description": "" if d.get("description") is None else str(d.get("description")),
                "related_ticket_id": "" if d.get("related_ticket_id") is None else str(d.get("related_ticket_id")),
                "space_key": "" if d.get("space_key") is None else str(d.get("space_key")),
                "status": "" if d.get("status") is None else str(d.get("status")),
                "created_at": "" if d.get("created_at") is None else str(d.get("created_at")),
                "updated_at": "" if d.get("updated_at") is None else str(d.get("updated_at"))
            })

        return json.dumps({
            "success": True,
            "pages": pages,
            "returned_count": len(pages),
            "matched_count": len(matched),
            "message": "Pages retrieved successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_pages",
                "description": (
                    " Retrieves Confluence-style documentation pages by querying a specific search field. Can also return a list of all pages if no search parameters are provided.\n"
                    " Purpose: To filter and retrieve knowledge base content such as runbooks, incident briefs, policies, or procedural documentation based on exact matches or regex patterns.\n"
                    " When to use: Use this tool when you need to find one or multiple documentation pages using specific criteria, such as matching a title, finding pages related to a ticket ID, searching within descriptions, or getting a generic list of pages.\n"
                    " Returns: Returns a JSON string containing a success boolean, a list of matching page dictionaries with their metadata, the returned count, and a success message text. "
                    "Default behavior: 'limit' defaults to 25 if not provided. If 'search_field' and 'query' are omitted, it lists all available pages up to the limit. "
                    "Regex search is supported and evaluated (case-insensitive) for the following search_fields: 'page_name', 'title', 'description', and 'status'. "
                    "Exact string match is strictly required for the following search_fields: 'page_id', 'related_ticket_id', 'space_key', 'created_at', and 'updated_at'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_field": {
                            "type": "string",
                            "enum": [
                                "page_id",
                                "page_name",
                                "title",
                                "description",
                                "related_ticket_id",
                                "space_key",
                                "status",
                                "created_at",
                                "updated_at"
                            ],
                            "description": "The specific field to search within. Optional; if omitted alongside query, the tool lists all pages."
                        },
                        "query": {
                            "type": "string",
                            "description": "The value or regex pattern to search for in the specified search field. Regex is supported for page_name, title, description, and status. Exact match is used for page_id, related_ticket_id, space_key, created_at, and updated_at. Optional; if omitted alongside search_field, the tool lists all pages."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of pages to return. Default is 25."
                        }
                    },
                    "required": []
                }
            }
        }
