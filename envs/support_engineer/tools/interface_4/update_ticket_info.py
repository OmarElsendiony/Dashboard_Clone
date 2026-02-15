import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateTicketInfo(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: Optional[str] = None,
        ticket_number: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not any([ticket_id, ticket_number]):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one identifier must be provided: ticket_id or ticket_number",
                }
            )

        if not any([status, priority, assigned_to]):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one field to update must be provided: status, priority, or assigned_to",
                }
            )

        tickets = data.get("tickets", {})

        target_ticket = None

        if ticket_id:
            if str(ticket_id) in tickets:
                target_ticket = tickets[str(ticket_id)]
            else:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Ticket with id '{ticket_id}' not found",
                    }
                )
        elif ticket_number:
            for ticket in tickets.values():
                if ticket.get("ticket_number") == ticket_number:
                    target_ticket = ticket
                    break
            if not target_ticket:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Ticket with number '{ticket_number}' not found",
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
            target_ticket["status"] = status

        if priority is not None:
            valid_priorities = ["P1", "P2", "P3"]
            if priority not in valid_priorities:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid priority '{priority}'. Valid values: P1, P2, P3",
                    }
                )
            target_ticket["priority"] = priority

        if assigned_to is not None:
            users = data.get("users", {})
            if str(assigned_to) not in users:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User with id '{assigned_to}' not found",
                    }
                )
            user = users[str(assigned_to)]
            if user.get("status") != "active":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User with id '{assigned_to}' is not active. Current status: {user.get('status')}",
                    }
                )
            target_ticket["assigned_to"] = assigned_to

        static_timestamp = "2026-02-02 23:59:00"
        target_ticket["updated_at"] = static_timestamp

        _EXCLUDE_KEYS = {
            "ingestion_channel",
            "kb_article_link",
            "incident_timestamp",
            "escalation_reason",
            "created_at",
        }
        _EXCLUDE_PREFIXES = ("incident_", "escalation_", "space_")
        ticket_response = {
            k: v
            for k, v in target_ticket.items()
            if k not in _EXCLUDE_KEYS and not k.startswith(_EXCLUDE_PREFIXES)
        }
        return json.dumps({"success": True, "ticket": ticket_response})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_ticket_info",
                "description": "Update a ticket's status, priority, or assignment.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket identifier",
                        },
                        "ticket_number": {
                            "type": "string",
                            "description": "Ticket number",
                        },
                        "status": {
                            "type": "string",
                            "description": "New ticket status",
                            "enum": ["open", "closed", "pending", "in_progress"],
                        },
                        "priority": {
                            "type": "string",
                            "description": "New ticket priority",
                            "enum": ["P1", "P2", "P3"],
                        },
                        "assigned_to": {
                            "type": "string",
                            "description": "User identifier to assign ticket to",
                        },
                    },
                    "required": [],
                    "oneOf": [
                        {"required": ["ticket_id"]},
                        {"required": ["ticket_number"]},
                    ],
                    "anyOf": [
                        {"required": ["status"]},
                        {"required": ["priority"]},
                        {"required": ["assigned_to"]},
                    ],
                },
            },
        }
