import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class AssignTicketToMember(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        user_id: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not ticket_id:
            return json.dumps({"success": False, "error": "ticket_id is required"})

        if not user_id:
            return json.dumps({"success": False, "error": "user_id is required"})

        tickets = data.get("tickets", {})
        users = data.get("users", {})

        if str(ticket_id) not in tickets:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Ticket with id '{ticket_id}' not found",
                }
            )

        if str(user_id) not in users:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with id '{user_id}' not found",
                }
            )

        user = users[str(user_id)]
        user_status = user.get("status")

        if user_status != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with id '{user_id}' is not active. Current status: {user_status}",
                }
            )

        ticket = tickets[str(ticket_id)]
        ticket_status = ticket.get("status")
        if ticket_status in ("closed"):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Ticket '{ticket_id}' cannot be assigned: ticket is {ticket_status}. Only open, pending, or in_progress tickets can be assigned.",
                }
            )

        current_assignee = ticket.get("assigned_to")
        if current_assignee is not None and str(current_assignee).strip():
            return json.dumps(
                {
                    "success": False,
                    "error": f"Ticket '{ticket_id}' is already assigned to user '{current_assignee}'. Halt and transfer to human for re-assignment.",
                }
            )

        ticket_tags = data.get("ticket_tags", {})
        tags = data.get("tags", {})
        tag_lookup = {
            str(tag.get("tag_id")): tag.get("tag_name") for tag in tags.values()
        }
        ticket_tag_names = []
        for ticket_tag in ticket_tags.values():
            if str(ticket_tag.get("ticket_id")) == str(ticket_id):
                tag_id = ticket_tag.get("tag_id")
                tag_name = tag_lookup.get(str(tag_id)) if tag_id is not None else None
                if tag_name:
                    ticket_tag_names.append(tag_name)
        if "awaiting_customer" in ticket_tag_names:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Ticket '{ticket_id}' has tag 'awaiting_customer'. Assignment is forbidden until the tag is removed.",
                }
            )

        static_timestamp = "2026-02-02 23:59:00"

        ticket["assigned_to"] = user_id
        ticket["updated_at"] = static_timestamp

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
            for k, v in ticket.items()
            if k not in _EXCLUDE_KEYS and not k.startswith(_EXCLUDE_PREFIXES)
        }
        return json.dumps(
            {
                "success": True,
                "ticket": ticket_response,
                "assigned_user": {
                    "user_id": user.get("user_id"),
                    "username": user.get("username"),
                    "email": user.get("email"),
                    "role": user.get("role"),
                    "technical_expertise": user.get("technical_expertise"),
                },
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "assign_ticket_to_member",
                "description": "Assign a ticket to a support team member for handling and resolution.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket identifier to assign",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User identifier of the team member",
                        },
                    },
                    "required": ["ticket_id", "user_id"],
                },
            },
        }
