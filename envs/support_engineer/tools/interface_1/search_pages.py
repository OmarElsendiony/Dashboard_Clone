import json
import shlex
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class SearchPages(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        cql: str,
        limit: Optional[int] = 25,
        space_key: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not cql:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'cql' is required."
            })

        if not isinstance(cql, str) or not cql.strip():
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: cql must be a non-empty string."
            })

        if limit is None:
            limit = 25

        if not isinstance(limit, int) or limit <= 0:
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: limit must be a positive integer."
            })

        if space_key is not None and (not isinstance(space_key, str) or not space_key.strip()):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: space_key must be a non-empty string when provided."
            })

        if status is not None and (not isinstance(status, str) or not status.strip()):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: status must be a non-empty string when provided."
            })

        documents = data.get("documents", {})
        if not isinstance(documents, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'documents' must be a dictionary"
            })

        try:
            tokens = shlex.split(cql)
        except Exception:
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: malformed CQL query."
            })

        groups = [[]]
        order_by = None
        order_dir = "asc"

        i = 0
        while i < len(tokens):
            t = tokens[i].lower()

            if t == "order" and i + 1 < len(tokens) and tokens[i + 1].lower() == "by":
                if i + 2 < len(tokens):
                    order_by = tokens[i + 2]
                if i + 3 < len(tokens) and tokens[i + 3].lower() in ["asc", "desc"]:
                    order_dir = tokens[i + 3].lower()
                break

            if t == "or":
                groups.append([])
                i += 1
                continue

            if t == "and":
                i += 1
                continue

            field = ""
            op = ""
            value = ""

            if i + 2 < len(tokens) and tokens[i + 1] in ["=", "~"]:
                field = tokens[i]
                op = tokens[i + 1]
                value = tokens[i + 2]
                i += 3
            else:
                if "=" in tokens[i]:
                    parts = tokens[i].split("=", 1)
                    field = parts[0]
                    value = parts[1]
                    op = "="
                    i += 1
                elif "~" in tokens[i]:
                    parts = tokens[i].split("~", 1)
                    field = parts[0]
                    value = parts[1]
                    op = "~"
                    i += 1
                else:
                    field = "keyword"
                    value = tokens[i]
                    op = "keyword"
                    i += 1

            groups[-1].append({
                "field": field.lower(),
                "op": op,
                "value": value.lower()
            })

        sk = space_key.lower() if isinstance(space_key, str) else ""
        st = status.lower() if isinstance(status, str) else ""

        matched = []

        for doc in documents.values():
            if not isinstance(doc, dict):
                continue

            if sk and str(doc.get("space_key", "")).lower() != sk:
                continue

            if st and str(doc.get("status", "")).lower() != st:
                continue

            title = str(doc.get("title", "")).lower()
            body = str(doc.get("description", "")).lower()

            doc_match = False

            for group in groups:
                group_ok = True
                for clause in group:
                    field = clause["field"]
                    op = clause["op"]
                    val = clause["value"]

                    if field == "keyword":
                        if val not in title and val not in body:
                            group_ok = False
                            break
                        continue

                    if field in ["text", "content", "body", "description"]:
                        target = body
                    elif field == "title":
                        target = title
                    elif field == "space":
                        target = str(doc.get("space_key", "")).lower()
                    elif field == "status":
                        target = str(doc.get("status", "")).lower()
                    elif field in ["id", "document_id"]:
                        target = str(doc.get("document_id", "")).lower()
                    else:
                        target = str(doc.get(field, "")).lower()

                    if op == "=" and target != val:
                        group_ok = False
                        break
                    if op == "~" and val not in target:
                        group_ok = False
                        break

                if group_ok:
                    doc_match = True
                    break

            if doc_match:
                matched.append(doc)

        if order_by:
            matched.sort(
                key=lambda d: str(d.get(order_by, "")).lower(),
                reverse=(order_dir == "desc")
            )
        else:
            matched.sort(
                key=lambda d: (str(d.get("title", "")).lower(), str(d.get("document_id", "")))
            )

        matched = matched[:limit]

        pages = []
        for d in matched:
            pages.append({
                "page_id": str(d.get("document_id", "")),
                "title": d.get("title", ""),
                "description": d.get("description", ""),
                "related_ticket_id": d.get("related_ticket_id", ""),
                "space_key": d.get("space_key", ""),
                "status": d.get("status", ""),
                "created_at": d.get("created_at", ""),
                "updated_at": d.get("updated_at", ""),
            })

        return json.dumps({
            "success": True,
            "pages": pages,
            "returned_count": len(pages),
            "matched_count": len(matched),
            "message": "Pages searched successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "search_pages",
                "description": (
                    "Searches Confluence-style documentation pages using a CQL query. Use this tool when the goal is "
                    "to discover relevant knowledge base content such as runbooks, incident briefs, policies, or "
                    "procedural documentation across draft and published spaces, rather than retrieving a single "
                    "known page by identifier. The tool evaluates keyword terms, field-based filters, logical AND/OR "
                    "conditions, and optional ordering to return matching page records with metadata so downstream "
                    "steps can select the correct page to open or reference."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cql": {
                            "type": "string",
                            "description": "CQL query used to search pages."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of pages to return (optional )"
                        },
                        "space_key": {
                            "type": "string",
                            "enum": ["Drafts_Space", "Public_KB_Space"],
                            "description": "Restrict search results to a specific documentation space (optional )"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["WIP", "Verified", "Archived"],
                            "description": "Restrict search results to a specific documentation status (optional )"
                        }
                    },
                    "required": ["cql"]
                }
            }
        }
