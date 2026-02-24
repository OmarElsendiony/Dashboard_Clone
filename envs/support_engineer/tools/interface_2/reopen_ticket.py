import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ReopenTicket(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
    ) -> str:
        timestamp = "2026-02-02 23:59:00"

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        if not ticket_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'ticket_id'"})

        # Get data containers
        tickets_dict = data.get("tickets", {})

        # Convert and validate inputs
        ticket_id_str = str(ticket_id).strip()

        # Check if ticket exists
        if ticket_id_str not in tickets_dict:
            return json.dumps({
                "success": False,
                "error": f"Ticket with ID '{ticket_id_str}' not found"
            })

        ticket = tickets_dict[ticket_id_str]

        # Validate ticket is a dict
        if not isinstance(ticket, dict):
            return json.dumps({
                "success": False,
                "error": f"Invalid ticket data structure for ticket ID '{ticket_id_str}'"
            })

        # Get current ticket status
        current_status = str(ticket.get("status", ""))

        # Validate current status exists
        if not current_status:
            return json.dumps({
                "success": False,
                "error": f"Ticket '{ticket_id_str}' has no status field"
            })

        current_status_str = str(current_status).strip()

        # Validate ticket can be reopened (must be in closed status)
        valid_statuses_for_reopen = ["closed"]

        if current_status_str not in valid_statuses_for_reopen:
            return json.dumps({
                "success": False,
                "error": f"Ticket '{ticket_id_str}' cannot be reopened. Current status is '{current_status_str}'. Only tickets with status 'closed' can be reopened."
            })

        if current_status_str == "archived":
            return json.dumps({
                "success": False,
                "error": f"Ticket '{ticket_id_str}' is archived and cannot be reopened"
            })

        # Update ticket status to open
        ticket["status"] = "open"
        ticket["updated_at"] = timestamp

        # Clear resolved_at and closed_at timestamps since ticket is being reopened
        if "resolved_at" in ticket:
            ticket["resolved_at"] = None
        if "closed_at" in ticket:
            ticket["closed_at"] = None

        # Build success message
        message = f"Ticket '{ticket.get('ticket_number', ticket_id_str)}' has been successfully reopened"

        return json.dumps({
            "success": True,
            "ticket": ticket,
            "message": message
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "reopen_ticket",
                "description": (
                    "Reopens a previously closed support ticket and restores it to an open state. "
                    "This function transitions a ticket from 'closed' status back to 'open' status, "
                    "allowing further investigation and resolution activities to continue. "
                    "Use this when a closed ticket needs to be worked on again due to issue recurrence, "
                    "incomplete resolution, or new related information."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The unique identifier of the ticket to reopen.",
                        },
                    },
                    "required": ["ticket_id"],
                },
            },
        }
