import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ListTickets(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: Optional[str] = None,
        ticket_number: Optional[str] = None,
        customer_id: Optional[str] = None,
        assigned_to: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        title: Optional[str] = None,
        created_after: Optional[str] = None,
        limit: int = 10,
    ) -> str:
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return json.dumps({
                    "success": bool(False),
                    "error": str("Wrong data format"),
                })
        if not isinstance(data, dict):
            return json.dumps({
                "success": bool(False),
                "error": str("Wrong data format"),
            })

        if priority is not None:
            valid_priorities = ["P1", "P2", "P3"]
            if priority not in valid_priorities:
                return json.dumps({
                    "success": bool(False),
                    "error": str(f"Invalid priority \"{priority}\". Valid values: P1, P2, P3"),
                })

        if status is not None:
            valid_statuses = ["open", "closed", "pending", "in_progress"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": bool(False),
                    "error": str(f"Invalid status \"{status}\". Valid values: {', '.join(valid_statuses)}"),
                })

        tickets = data.get("tickets", {})
        ticket_tags = data.get("ticket_tags", {})
        tags = data.get("tags", {})

        tag_lookup = {
            str(tag.get("tag_id")): str(tag.get("tag_name", "")) for tag in tags.values()
        }

        results = []
        for ticket in tickets.values():
            if ticket_id is not None and str(ticket.get("ticket_id")) != str(ticket_id):
                continue

            if ticket_number is not None and str(ticket.get("ticket_number")) != str(ticket_number):
                continue

            if customer_id is not None and str(ticket.get("customer_id")) != str(customer_id):
                continue

            if assigned_to is not None:
                ticket_assigned_to = ticket.get("assigned_to")
                if ticket_assigned_to is None or str(ticket_assigned_to) != str(assigned_to):
                    continue

            if status is not None and str(ticket.get("status")) != str(status):
                continue

            if priority is not None and str(ticket.get("priority")) != str(priority):
                continue

            if title is not None and str(title).lower() not in str(ticket.get("title", "")).lower():
                continue

            if created_after is not None:
                ticket_created_at = str(ticket.get("created_at", ""))
                if ticket_created_at < str(created_after):
                    continue

            ticket_tag_list = []
            for ticket_tag in ticket_tags.values():
                if str(ticket_tag.get("ticket_id")) == str(ticket.get("ticket_id")):
                    tag_id = ticket_tag.get("tag_id")
                    tag_name = tag_lookup.get(str(tag_id)) if tag_id is not None else None
                    if tag_name:
                        ticket_tag_list.append(str(tag_name))

            ticket_id_val = ticket.get("ticket_id")
            ticket_number_val = ticket.get("ticket_number")
            customer_id_val = ticket.get("customer_id")
            assigned_to_val = ticket.get("assigned_to")
            title_val = ticket.get("title")
            description_val = ticket.get("description")
            priority_val = ticket.get("priority")
            status_val = ticket.get("status")
            created_at_val = ticket.get("created_at")
            updated_at_val = ticket.get("updated_at")
            resolved_at_val = ticket.get("resolved_at")
            closed_at_val = ticket.get("closed_at")

            filtered_ticket = {
                "ticket_id": str(ticket_id_val) if ticket_id_val is not None else None,
                "ticket_number": str(ticket_number_val) if ticket_number_val is not None else None,
                "customer_id": str(customer_id_val) if customer_id_val is not None else None,
                "assigned_to": str(assigned_to_val) if assigned_to_val is not None else None,
                "title": str(title_val) if title_val is not None else None,
                "description": str(description_val) if description_val is not None else None,
                "priority": str(priority_val) if priority_val is not None else None,
                "status": str(status_val) if status_val is not None else None,
                "created_at": str(created_at_val) if created_at_val is not None else None,
                "updated_at": str(updated_at_val) if updated_at_val is not None else None,
                "resolved_at": str(resolved_at_val) if resolved_at_val is not None else None,
                "closed_at": str(closed_at_val) if closed_at_val is not None else None,
                "tags": [str(tag) for tag in ticket_tag_list],
            }

            results.append(filtered_ticket)

        if limit is not None:
            limit_int = int(limit)
            if limit_int > 0:
                results = results[:limit_int]

        return json.dumps({
            "success": bool(True),
            "tickets": results,
            "count": int(len(results)),
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_tickets",
                "description": "Lists tickets matching specified filter criteria.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Filter by ticket identifier",
                        },
                        "ticket_number": {
                            "type": "string",
                            "description": "Filter by ticket number",
                        },
                        "customer_id": {
                            "type": "string",
                            "description": "Filter by customer identifier",
                        },
                        "assigned_to": {
                            "type": "string",
                            "description": "Filter by assignee identifier",
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by ticket status",
                            "enum": ["open", "closed", "pending", "in_progress"],
                        },
                        "priority": {
                            "type": "string",
                            "description": "Filter by ticket priority",
                            "enum": ["P1", "P2", "P3"],
                        },
                        "title": {
                            "type": "string",
                            "description": "Filter by title substring",
                        },
                        "created_after": {
                            "type": "string",
                            "description": "Filter by creation timestamp",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of tickets to return. Defaults to 10.",
                        },
                    },
                    "required": [],
                },
            },
        }
