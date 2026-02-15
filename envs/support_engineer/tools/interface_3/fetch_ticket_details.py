import json
from typing import Dict, Optional, Any
from tau_bench.envs.tool import Tool


class FetchTicketDetails(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_number: Optional[str] = None,
        ticket_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        if not ticket_number and not ticket_id:
            return json.dumps({"error": "Either ticket_number or ticket_id must be provided"})

        valid_statuses = ("open", "awaiting_info", "ready_for_investigation", "root_cause_identified", "in_progress", "escalated", "resolved", "fix_rejected")
        if status and status not in valid_statuses:
            return json.dumps(
                {"error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"}
            )

        tickets = data.get("tickets", {})
        ticket_tags = data.get("ticket_tags", {})
        tags = data.get("tags", {})

        found_ticket_id = None
        ticket_details = None

        if ticket_number is not None and ticket_id is not None:
            ticket_details = tickets.get(str(ticket_id))
            if not ticket_details:
                return json.dumps({"error": f"Ticket with ID '{ticket_id}' not found"})
            if ticket_details.get("ticket_number") != str(ticket_number):
                return json.dumps(
                    {"error": f"Mismatch: ticket_id '{ticket_id}' does not correspond to ticket_number '{ticket_number}'"}
                )
            found_ticket_id = ticket_id

        elif ticket_id is not None:
            ticket_details = tickets.get(str(ticket_id))
            if not ticket_details:
                return json.dumps({"error": f"Ticket with ID '{ticket_id}' not found"})
            found_ticket_id = ticket_id

        else:
            for t_id, t_details in tickets.items():
                if t_details.get("ticket_number") == ticket_number:
                    found_ticket_id = t_id
                    ticket_details = t_details
                    break
            if not ticket_details:
                return json.dumps({"error": f"Ticket with number '{ticket_number}' not found"})

        if status and ticket_details.get("status") != status:
            return json.dumps(
                {"error": f"Ticket '{found_ticket_id}' does not have status '{status}'"}
            )

        ticket_tag_list = [
            {
                "tag_id": int(tt.get("tag_id")),
                "tag_type": str(tt.get("tag_type")),
                "tag_name": str(tags.get(str(tt.get("tag_id")), {}).get("tag_name", "")),
            }
            for tt in ticket_tags.values()
            if str(tt.get("ticket_id")) == str(found_ticket_id)
        ]

        return json.dumps({
            "success": True,
            "ticket_details": {
                "ticket_id": str(ticket_details["ticket_id"]),
                "ticket_number": str(ticket_details["ticket_number"]),
                "customer_id": str(ticket_details["customer_id"]) if ticket_details.get("customer_id") else None,
                "title": str(ticket_details["title"]),
                "description": str(ticket_details["description"]),
                "status": str(ticket_details["status"]),
                "escalation_reason": str(ticket_details["escalation_reason"]) if ticket_details.get("escalation_reason") else None,
                "created_at": str(ticket_details["created_at"]),
                "updated_at": str(ticket_details["updated_at"]),
                "closed_at": str(ticket_details["closed_at"]) if ticket_details.get("closed_at") else None,
                "tags": ticket_tag_list,
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_ticket_details",
                "description": "Retrieves a ticket's details along with the ticket tags from the ticketing system. This should be used when you need to look up specific information about a ticket.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_number": {
                            "type": "string",
                            "description": "The number of the ticket to look up",
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "The unique identifier of the ticket to look up",
                        },
                        "status": {
                            "type": "string",
                            "description": "The expected status of the ticket",
                            "enum": ["open", "awaiting_info", "ready_for_investigation", "root_cause_identified", "in_progress", "escalated", "resolved", "fix_rejected"],
                        },
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["ticket_number"]},
                        {"required": ["ticket_id"]},
                    ],
                },
            },
        }
