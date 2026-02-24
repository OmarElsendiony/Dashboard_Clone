import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetTickets(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        search_field: str,
        query: str,
        limit: Optional[int] = 25,
        sort_by: Optional[str] = "updated_at",
        sort_order: Optional[str] = "desc",
        include_tags: Optional[bool] = False,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not search_field or not isinstance(search_field, str):
            return json.dumps({"success": False, "error": "Missing Argument: 'search_field' is required."})

        if not query or not str(query).strip():
            return json.dumps({"success": False, "error": "Missing Argument: 'query' must be a non-empty string."})

        if limit is None:
            limit = 25
        elif not isinstance(limit, int) or limit <= 0:
            return json.dumps({"success": False, "error": "Invalid Argument: limit must be a positive integer."})

        if sort_order is None:
            sort_order = "desc"
        elif sort_order not in ["asc", "desc"]:
            return json.dumps({"success": False, "error": "Invalid Argument: sort_order must be 'asc' or 'desc'."})

        if sort_by is None:
            sort_by = "updated_at"

        if include_tags is None:
            include_tags = False
        elif not isinstance(include_tags, bool):
            return json.dumps({"success": False, "error": "Invalid Argument: include_tags must be a boolean."})

        tickets = data.get("tickets", {})
        if not isinstance(tickets, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'tickets' must be a dictionary"})

        ticket_to_tags = {}
        if include_tags:
            ticket_tags = data.get("ticket_tags", {})
            tags = data.get("tags", {})

            tag_id_to_name = {}
            if isinstance(tags, dict):
                for v in tags.values():
                    if isinstance(v, dict):
                        tid = str(v.get("tag_id", "")).strip()
                        name = str(v.get("tag_name", "")).strip().lower()
                        if tid and name:
                            tag_id_to_name[tid] = name

            if isinstance(ticket_tags, dict):
                for row in ticket_tags.values():
                    if not isinstance(row, dict):
                        continue
                    tid = str(row.get("ticket_id", "")).strip()
                    tag_id = str(row.get("tag_id", "")).strip()
                    if tid and tag_id in tag_id_to_name:
                        if tid not in ticket_to_tags:
                            ticket_to_tags[tid] = set()
                        ticket_to_tags[tid].add(tag_id_to_name[tag_id])

        valid_fields = [
            "ticket_id", "ticket_number", "customer_id", "assigned_to",
            "title", "description", "priority", "status", "escalation_reason",
            "ingestion_channel", "incident_timestamp", "created_at",
            "updated_at", "resolved_at", "closed_at"
        ]

        if search_field not in valid_fields:
            return json.dumps({
                "success": False,
                "error": f"Invalid search_field '{search_field}'. Valid fields are: {', '.join(valid_fields)}"
            })

        results = []
        normalized_query = str(query).strip().lower()
        exact_match_fields = {
            "ticket_id", "ticket_number", "customer_id", "assigned_to",
            "priority", "status", "ingestion_channel", "escalation_reason"
        }

        for ticket in tickets.values():
            if not isinstance(ticket, dict):
                continue

            field_value = ticket.get(search_field)
            if field_value is None:
                continue

            normalized_field_value = str(field_value).strip().lower()
            matched = False

            if search_field in exact_match_fields:
                if normalized_field_value == normalized_query:
                    matched = True
            else:
                if normalized_query in normalized_field_value:
                    matched = True

            if matched:
                out = dict(ticket)
                if include_tags:
                    ticket_id_str = str(ticket.get("ticket_id", "")).strip()
                    tag_set = ticket_to_tags.get(ticket_id_str, set())
                    out["tags"] = sorted(list(tag_set))
                results.append(out)

        def get_sort_key(item):
            val = item.get(sort_by, "")
            if sort_by in ["ticket_id", "customer_id"]:
                try:
                    return int(val)
                except (ValueError, TypeError):
                    return str(val).lower()
            return str(val).lower()

        results.sort(key=get_sort_key, reverse=(sort_order == "desc"))

        results = results[:limit]

        final_tickets = []
        for t in results:
            new_t = {
                "ticket_id": str(t.get("ticket_id", "")),
                "ticket_number": str(t.get("ticket_number", "")),
                "customer_id": str(t.get("customer_id", "")),
                "title": str(t.get("title", "")),
                "description": str(t.get("description", "")),
                "status": str(t.get("status", "")),
                "priority": str(t.get("priority", "")),
                "ingestion_channel": str(t.get("ingestion_channel", "")),
                "created_at": str(t.get("created_at", "")),
                "updated_at": str(t.get("updated_at", ""))
            }
            if include_tags:
                new_t["tags"] = [str(tag) for tag in t.get("tags", [])]
            final_tickets.append(new_t)

        return json.dumps({
            "success": True,
            "tickets": final_tickets,
            "returned_count": len(final_tickets),
            "matched_count": len(results),
            "message": "Tickets searched successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_tickets",
                "description": (
                    "Retrieves ticket records from the database based on a specific field and query. "
                    "Performs exact, case-insensitive matching for strict categorical/ID fields (ticket_id, ticket_number, customer_id, assigned_to, priority, status, ingestion_channel, escalation_reason). "
                    "Performs case-insensitive substring matching for unstructured text fields (title, description, timestamps). "
                    "Purpose: Enables discovery, correlation, and deduplication of tickets based on specific attributes or keywords. "
                    "When to use: During ticket intake, duplicate detection, incident investigation, SLA checks, or escalation workflows. "
                    "Returns: A list of matching ticket records with metadata for downstream actions such as merging, updating, or linking issues."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_field": {
                            "type": "string",
                            "description": "The specific field in the tickets table to search against (e.g., 'ticket_number', 'status', 'priority', 'customer_id', 'title')."
                        },
                        "query": {
                            "type": "string",
                            "description": "The value to search for. Case-insensitive."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of tickets to return (optional). Default is 25."
                        },
                        "sort_by": {
                            "type": "string",
                            "description": "Ticket field used for sorting results (optional). Default is 'updated_at'."
                        },
                        "sort_order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "description": "Sort direction for search results (optional). Default is 'desc'."
                        },
                        "include_tags": {
                            "type": "boolean",
                            "description": "Include resolved tag names in each returned ticket (optional). Default is False."
                        }
                    },
                    "required": ["search_field", "query"]
                }
            }
        }
