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
        if isinstance(data, str):
            data = json.loads(data)
        if not isinstance(data, dict):
            return json.dumps({"success": bool(False), "error": str("Invalid data format")})
        if ticket_id is None or ticket_id == "":
            return json.dumps({"success": bool(False), "error": str("ticket_id is required")})
        if user_id is None or user_id == "":
            return json.dumps({"success": bool(False), "error": str("user_id is required")})

        tickets = data.get("tickets", {})
        users = data.get("users", {})

        if str(ticket_id) not in tickets:
            return json.dumps(
                {
                    "success": bool(False),
                    "error": str(f"Ticket with id \"{ticket_id}\" not found"),
                }
            )
        if str(user_id) not in users:
            return json.dumps(
                {
                    "success": bool(False),
                    "error": str(f"User with id \"{user_id}\" not found"),
                }
            )

        user = users[str(user_id)]
        user_status = user.get("status")
        if user_status != "active":
            return json.dumps(
                {
                    "success": bool(False),
                    "error": str(f"User with id \"{user_id}\" is not active. Current status: {user_status}"),
                }
            )

        ticket = tickets[str(ticket_id)]
        ticket_status = ticket.get("status")
        if ticket_status == "closed":
            return json.dumps(
                {
                    "success": bool(False),
                    "error": str(f"Ticket \"{ticket_id}\" cannot be assigned: ticket is {ticket_status}. Only open, pending, or in_progress tickets can be assigned."),
                }
            )

        current_assignee = ticket.get("assigned_to")
        if current_assignee is not None and str(current_assignee).strip():
            return json.dumps(
                {
                    "success": bool(False),
                    "error": str(f"Ticket \"{ticket_id}\" is already assigned to user \"{current_assignee}\". Halt and transfer to human for re-assignment."),
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
                    "success": bool(False),
                    "error": str(f"Ticket \"{ticket_id}\" has tag 'awaiting_customer'. Assignment is forbidden until the tag is removed."),
                }
            )

        static_timestamp = "2026-02-02 23:59:00"
        ticket["assigned_to"] = user_id
        ticket["updated_at"] = static_timestamp

        exclude_keys = {
            "ingestion_channel",
            "kb_article_link",
            "incident_timestamp",
            "escalation_reason",
            "created_at",
        }
        exclude_prefixes = ("incident_", "escalation_", "space_")
        ticket_response = {}
        for k, v in ticket.items():
            if k not in exclude_keys and not k.startswith(exclude_prefixes):
                if v is None:
                    ticket_response[k] = None
                elif isinstance(v, bool):
                    ticket_response[k] = bool(v)
                elif isinstance(v, int):
                    ticket_response[k] = int(v)
                elif isinstance(v, float):
                    ticket_response[k] = int(v) if v == int(v) else float(v)
                else:
                    ticket_response[k] = str(v)

        u_id = user.get("user_id")
        username = user.get("username")
        email = user.get("email")
        role = user.get("role")
        tech_exp = user.get("technical_expertise")
        if isinstance(tech_exp, list):
            tech_exp_out = [str(x) for x in tech_exp]
        else:
            tech_exp_out = str(tech_exp) if tech_exp is not None else None
        assigned_user = {
            "user_id": str(u_id) if u_id is not None else None,
            "username": str(username) if username is not None else None,
            "email": str(email) if email is not None else None,
            "role": str(role) if role is not None else None,
            "technical_expertise": tech_exp_out,
        }

        return json.dumps(
            {
                "success": bool(True),
                "ticket": ticket_response,
                "assigned_user": assigned_user,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "assign_ticket_to_member",
                "description": "Assigns a ticket to a support team member for handling and resolution.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket identifier to assign.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User identifier of the team member.",
                        },
                    },
                    "required": ["ticket_id", "user_id"],
                },
            },
        }
