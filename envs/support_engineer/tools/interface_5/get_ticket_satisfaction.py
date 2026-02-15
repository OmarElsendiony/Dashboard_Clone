import json
from typing import Dict, Optional
from tau_bench.envs.tool import Tool


class GetTicketSatisfaction(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, object],
        ticket_id: Optional[str] = None,
        ticket_number: Optional[str] = None
    ) -> str:
        tickets = data.get("tickets", {})
        customer_feedback = data.get("customer_feedback", {})

        # Resolve ticket_id from ticket_number if needed
        if ticket_number and not ticket_id:
            for ticket in tickets.values():
                if ticket.get("ticket_number") == ticket_number:
                    ticket_id = ticket.get("ticket_id")
                    break
            if not ticket_id:
                return json.dumps(
                    {"error": f"Ticket with number {ticket_number} not found"}
                )

        # Validate if both are provided
        if ticket_id and ticket_number:
            ticket = tickets.get(ticket_id)
            if ticket:
                if ticket.get("ticket_number") != ticket_number:
                    return json.dumps({
                        "error": f"Mismatch: ticket_id '{ticket_id}' corresponds to ticket_number '{ticket.get('ticket_number')}', not '{ticket_number}'"
                    })

        if not ticket_id:
            return json.dumps(
                {"error": "Either ticket_id or ticket_number must be provided"}
            )

        ticket = tickets.get(ticket_id)
        if not ticket:
            return json.dumps({"error": f"Ticket with ID {ticket_id} not found"})

        feedback_entries = [
            feedback
            for feedback in customer_feedback.values()
            if feedback.get("ticket_id") == ticket_id
        ]

        feedback_entries.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        # Calculate average score if there are feedback entries
        average_score = None
        if feedback_entries:
            scores = [
                entry.get("score")
                for entry in feedback_entries
                if entry.get("score") is not None
            ]
            if scores:
                average_score = sum(scores) / len(scores)

        return json.dumps(
            {
                "success": True,
                "ticket_id": str(ticket_id),
                "ticket_number": ticket.get("ticket_number"),
                "feedback_entries": feedback_entries,
                "total_feedback_entries": len(feedback_entries),
                "average_score": round(average_score, 2)
                if average_score is not None
                else None,
                "latest_feedback": feedback_entries[0] if feedback_entries else None,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, object]:
        return {
            "type": "function",
            "function": {
                "name": "get_ticket_satisfaction",
                "description": "Retrieve customer satisfaction feedback for a ticket including satisfaction scores, feedback text, and related information. Returns all feedback entries sorted by creation time (most recent first), along with the average satisfaction score and the latest feedback entry. Use this to understand customer satisfaction levels, review feedback, and assess the quality of support provided for a ticket. At least one of ticket_id or ticket_number must be provided.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Unique identifier of the ticket",
                        },
                        "ticket_number": {
                            "type": "string",
                            "description": "Ticket number in format TKT-000001",
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
