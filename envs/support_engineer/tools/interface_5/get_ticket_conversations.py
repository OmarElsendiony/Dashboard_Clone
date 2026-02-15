import json
from typing import Dict, Optional
from tau_bench.envs.tool import Tool


class GetTicketConversations(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, object],
        ticket_id: Optional[str] = None,
        ticket_number: Optional[str] = None
    ) -> str:
        tickets = data.get("tickets", {})
        ticket_comments = data.get("ticket_comments", {})
        customer_messages = data.get("customer_messages", {})

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
            
        if ticket_id and ticket_number:
            ticket = tickets.get(ticket_id)
            if ticket:
                if ticket.get("ticket_number") != ticket_number:
                    return json.dumps({
                        "error": f"Mismatch: ticket_id '{ticket_id}' corresponds to ticket_number '{ticket.get('ticket_number')}', not '{ticket_number}'"
                    })
            # If ticket doesn't exist, will be caught in next validation

        if not ticket_id:
            return json.dumps(
                {"error": "Either ticket_id or ticket_number must be provided"}
            )

        # Verify ticket exists
        ticket = tickets.get(ticket_id)
        if not ticket:
            return json.dumps({"error": f"Ticket with ID {ticket_id} not found"})

        # Get all comments for this ticket
        comments = [
            comment
            for comment in ticket_comments.values()
            if comment.get("ticket_id") == ticket_id
        ]

        # Get all customer messages for this ticket
        messages = [
            message
            for message in customer_messages.values()
            if message.get("ticket_id") == ticket_id
        ]

        # Sort by created_at timestamp
        comments.sort(key=lambda x: x.get("created_at", ""))
        messages.sort(key=lambda x: x.get("created_at", ""))

        return json.dumps(
            {
                "success": True,
                "ticket_id": str(ticket_id),
                "ticket_number": ticket.get("ticket_number"),
                "comments": comments,
                "customer_messages": messages,
                "total_comments": len(comments),
                "total_customer_messages": len(messages),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, object]:
        return {
            "type": "function",
            "function": {
                "name": "get_ticket_conversations",
                "description": "Retrieve all conversations for a ticket including public and private comments from agents/staff, as well as customer messages. Returns comments and customer messages sorted chronologically by creation time. Use this to review the full conversation history of a ticket for context, understanding customer interactions, agent responses, and the progression of the issue. At least one of ticket_id or ticket_number must be provided.",
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
