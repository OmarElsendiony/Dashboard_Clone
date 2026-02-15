import json
from typing import Dict
from tau_bench.envs.tool import Tool


class RetrieveTicket(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, object],
        ticket_id: str = None,
        ticket_number: str = None
    ) -> str:
        tickets = data.get("tickets", {})

        if ticket_id:
            ticket = tickets.get(ticket_id)
            if not ticket:
                return json.dumps({"error": f"Ticket with ID {ticket_id} not found"})
            return json.dumps({"success": True, "ticket": ticket})

        if ticket_number:
            for ticket in tickets.values():
                if ticket.get("ticket_number") == ticket_number:
                    return json.dumps({"success": True, "ticket": ticket})
            return json.dumps(
                {"error": f"Ticket with number {ticket_number} not found"}
            )

        return json.dumps(
            {"error": "Either ticket_id or ticket_number must be provided"}
        )

    @staticmethod
    def get_info() -> Dict[str, object]:
        return {
            "type": "function",
            "function": {
                "name": "retrieve_ticket",
                "description": "Retrieve complete ticket information including subject, description, priority, status, customer details, timestamps, and all associated metadata. Use this at the start of workflows to access ticket details for triage, investigation, or processing operations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Unique identifier of the ticket",
                        },
                        "ticket_number": {
                            "type": "string",
                            "description": "Ticket number in format TKT-XXXXXX",
                        },
                    },
                    "required": [],
                    "oneOf": [
                        {"required": ["ticket_id"]},
                        {"required": ["ticket_number"]},
                    ],
                },
            },
        }
