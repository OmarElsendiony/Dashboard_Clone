import json
import shlex
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class SearchTickets(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        query: str,
        limit: Optional[int] = 25,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "desc",
        status: Optional[str] = None,
        priority: Optional[str] = None,
        ingestion_channel: Optional[str] = None,
        include_tags: Optional[bool] = False,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not query:
             return json.dumps({"success": False, "error": "Missing Argument: 'query' is required."})

        if not isinstance(query, str) or not query.strip():
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: query must be a non-empty string."
            })

        if limit is None:
            limit = 25

        if not isinstance(limit, int) or limit <= 0:
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: limit must be a positive integer."
            })

        if sort_order is None:
            sort_order = "desc"

        if sort_order not in ["asc", "desc"]:
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: sort_order must be 'asc' or 'desc'."
            })

        if include_tags is None:
            include_tags = False

        if not isinstance(include_tags, bool):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: include_tags must be a boolean."
            })

        tickets = data.get("tickets", {})
        ticket_tags = data.get("ticket_tags", {})
        tags = data.get("tags", {})

        if not isinstance(tickets, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'tickets' must be a dictionary"
            })

        tag_id_to_name = {}
        if isinstance(tags, dict):
            for v in tags.values():
                if isinstance(v, dict):
                    tid = str(v.get("tag_id", "")).strip()
                    name = str(v.get("tag_name", "")).strip().lower()
                    if tid and name:
                        tag_id_to_name[tid] = name

        ticket_to_tags = {}
        if isinstance(ticket_tags, dict):
            for row in ticket_tags.values():
                if not isinstance(row, dict):
                    continue
                tid = str(row.get("ticket_id", "")).strip()
                tag_id = str(row.get("tag_id", "")).strip()
                if tid and tag_id in tag_id_to_name:
                    ticket_to_tags.setdefault(tid, set()).add(tag_id_to_name[tag_id])

        try:
            tokens = shlex.split(query)
        except Exception:
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: malformed Zendesk query."
            })

        groups = [[]]
        order_field = sort_by
        order_dir = sort_order

        i = 0
        while i < len(tokens):
            t = tokens[i].lower()

            if t == "order" and i + 1 < len(tokens) and tokens[i + 1].lower() == "by":
                if i + 2 < len(tokens):
                    order_field = tokens[i + 2]
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

            if i + 2 < len(tokens) and tokens[i + 1] in ["=", "~", ":"]:
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
                elif ":" in tokens[i]:
                    parts = tokens[i].split(":", 1)
                    field = parts[0]
                    value = parts[1]
                    op = "="
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

        results = []

        for ticket in tickets.values():
            if not isinstance(ticket, dict):
                continue

            if status is not None and str(ticket.get("status", "")).lower() != status.lower():
                continue

            if priority is not None and str(ticket.get("priority", "")).upper() != priority.upper():
                continue

            if ingestion_channel is not None and str(ticket.get("ingestion_channel", "")).lower() != ingestion_channel.lower():
                continue

            title = str(ticket.get("title", "")).lower()
            body = str(ticket.get("description", "")).lower()
            ticket_id = str(ticket.get("ticket_id", "")).strip()
            ticket_number = str(ticket.get("ticket_number", "")).lower()
            tag_set = ticket_to_tags.get(ticket_id, set())

            matched = False

            for group in groups:
                group_ok = True
                for clause in group:
                    field = clause["field"]
                    op = clause["op"]
                    val = clause["value"]

                    if field == "keyword":
                        if val not in title and val not in body and val not in ticket_number:
                            group_ok = False
                            break
                        continue

                    if field in ["title"]:
                        target = title
                    elif field in ["description", "text", "body"]:
                        target = body
                    elif field in ["status"]:
                        target = str(ticket.get("status", "")).lower()
                    elif field in ["priority"]:
                        target = str(ticket.get("priority", "")).lower()
                    elif field in ["channel", "ingestion_channel"]:
                        target = str(ticket.get("ingestion_channel", "")).lower()
                    elif field in ["ticket_id", "id"]:
                        target = ticket_id.lower()
                    elif field in ["ticket_number"]:
                        target = ticket_number
                    elif field in ["tag", "tags"]:
                        if op == "=" and val not in tag_set:
                            group_ok = False
                            break
                        if op == "~" and not any(val in t for t in tag_set):
                            group_ok = False
                            break
                        continue
                    else:
                        target = str(ticket.get(field, "")).lower()

                    if op == "=" and target != val:
                        group_ok = False
                        break
                    if op == "~" and val not in target:
                        group_ok = False
                        break

                if group_ok:
                    matched = True
                    break

            if matched:
                out = dict(ticket)
                if include_tags:
                    out["tags"] = sorted(list(tag_set))
                results.append(out)

        def get_sort_key(item):
            val = item.get(order_field, "")
            if order_field in ["ticket_id", "id", "customer_id"]:
                try:
                    return int(val)
                except (ValueError, TypeError):
                    return str(val).lower()
            return str(val).lower()

        if order_field:
            results.sort(
                key=get_sort_key,
                reverse=(order_dir == "desc")
            )
        else:
            results.sort(
                key=lambda t: str(t.get("updated_at", "")),
                reverse=(order_dir == "desc")
            )

        results = results[:limit]

        return json.dumps({
            "success": True,
            "tickets": results,
            "returned_count": len(results),
            "matched_count": len(results),
            "message": "Tickets searched successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "search_tickets",
                "description": (
                    "Searches support tickets using a structured query expression across ticket content and metadata."
                    "PURPOSE: Enables discovery, correlation, and deduplication of tickets based on keywords, attributes, and tags."
                    "WHEN TO USE: During ticket intake, duplicate detection, incident investigation, SLA checks, or escalation workflows."
                    "RETURNS: A list of matching ticket records with metadata for downstream actions such as merging, updating, or linking issues."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Zendesk Query Language search expression."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of tickets to return (optional)"
                        },
                        "sort_by": {
                            "type": "string",
                            "description": "Ticket field used for sorting results (optional)"
                        },
                        "sort_order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "description": "Sort direction for search results (optional)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter tickets by status (optional)"
                        },
                        "priority": {
                            "type": "string",
                            "description": "Filter tickets by priority (optional)"
                        },
                        "ingestion_channel": {
                            "type": "string",
                            "description": "Filter tickets by ingestion channel such as Web, Email, Phone, or Slack (optional)"
                        },
                        "include_tags": {
                            "type": "boolean",
                            "description": "Include resolved tag names in each returned ticket (optional)"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
