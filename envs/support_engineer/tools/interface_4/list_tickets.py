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
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if priority is not None:
            valid_priorities = ["P1", "P2", "P3"]
            if priority not in valid_priorities:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid priority '{priority}'. Valid values: {', '.join(valid_priorities)}",
                    }
                )

        if status is not None:
            valid_statuses = [
                "open", "closed", "pending", "in_progress"
            ]
            if status not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status}'. Valid values: {', '.join(valid_statuses)}",
                    }
                )

        tickets = data.get("tickets", {})
        ticket_tags = data.get("ticket_tags", {})
        tags = data.get("tags", {})

        tag_lookup = {
            str(tag.get("tag_id")): tag.get("tag_name") for tag in tags.values()
        }

        results = []
        for ticket in tickets.values():
            if ticket_id is not None and str(ticket.get("ticket_id")) != str(
                ticket_id
            ):
                continue

            if ticket_number is not None and ticket.get("ticket_number") != ticket_number:
                continue

            if customer_id is not None and str(ticket.get("customer_id")) != str(
                customer_id
            ):
                continue

            if assigned_to is not None:
                ticket_assigned_to = ticket.get("assigned_to")
                if ticket_assigned_to is None or str(ticket_assigned_to) != str(
                    assigned_to
                ):
                    continue

            if status is not None and ticket.get("status") != status:
                continue

            if priority is not None and ticket.get("priority") != priority:
                continue

            if title is not None and title.lower() not in ticket.get("title", "").lower():
                continue

            if created_after is not None:
                ticket_created_at = ticket.get("created_at", "")
                if ticket_created_at < created_after:
                    continue

            ticket_tag_list = []
            for ticket_tag in ticket_tags.values():
                if str(ticket_tag.get("ticket_id")) == str(ticket.get("ticket_id")):
                    tag_id = ticket_tag.get("tag_id")
                    tag_name = tag_lookup.get(str(tag_id)) if tag_id is not None else None
                    if tag_name:
                        ticket_tag_list.append(tag_name)

            filtered_ticket = {
                "ticket_id": ticket.get("ticket_id"),
                "ticket_number": ticket.get("ticket_number"),
                "customer_id": ticket.get("customer_id"),
                "assigned_to": ticket.get("assigned_to"),
                "title": ticket.get("title"),
                "description": ticket.get("description"),
                "priority": ticket.get("priority"),
                "status": ticket.get("status"),
                "created_at": ticket.get("created_at"),
                "updated_at": ticket.get("updated_at"),
                "resolved_at": ticket.get("resolved_at"),
                "closed_at": ticket.get("closed_at"),
                "tags": ticket_tag_list,
            }

            results.append(filtered_ticket)

        if limit is not None and limit > 0:
            results = results[:limit]

        return json.dumps({"success": True, "tickets": results, "count": len(results)})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_tickets",
                "description": "Search for tickets by identifier, customer, assignee, status, priority, or title.",
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
                            "enum": ["open", "closed", "pending", "in_progress"]
                        },
                        "priority": {
                            "type": "string",
                            "description": "Filter by ticket priority",
                            "enum": ["P1", "P2", "P3"]
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
                            "description": "Maximum number of tickets to return",
                        },
                    },
                    "required": [],
                },
            },
        }
