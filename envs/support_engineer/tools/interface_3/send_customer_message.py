import json
from typing import Dict, Any
from tau_bench.envs.tool import Tool


class SendCustomerMessage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_number: str,
        customer_email: str,
        message_type: str,
        message_content: str,
    ) -> str:
        if not ticket_number:
            return json.dumps({"error": "ticket_number is required"})

        if not customer_email:
            return json.dumps({"error": "customer_email is required"})

        if not message_type:
            return json.dumps({"error": "message_type is required"})

        if not message_content:
            return json.dumps({"error": "message_content is required"})

        valid_message_types = ("investigating", "root_cause_identified", "fix_in_progress", "awaiting_external", "resolved")
        if message_type not in valid_message_types:
            return json.dumps(
                {"error": f"Invalid message_type '{message_type}'. Must be one of: {', '.join(valid_message_types)}"}
            )

        tickets = data.get("tickets", {})
        customers = data.get("customers", {})
        customer_messages = data.get("customer_messages", {})
        timestamp = "2026-02-02 23:59:00"

        ticket_id = None
        for t_id, t_details in tickets.items():
            if t_details.get("ticket_number") == ticket_number:
                ticket_id = t_id
                break

        if not ticket_id:
            return json.dumps({"error": f"Ticket with number '{ticket_number}' not found"})

        customer_id = None
        for c_id, customer in customers.items():
            if customer.get("email") == str(customer_email):
                customer_id = c_id
                break

        if not customer_id:
            return json.dumps({"error": f"Customer with email '{customer_email}' not found"})

        if not customer_messages:
            message_id = "1"
        else:
            message_id = str(max(int(k) for k in customer_messages.keys()) + 1)

        new_message = {
            "message_id": str(message_id),
            "ticket_id": str(ticket_id),
            "customer_id": str(customer_id),
            "message_type": str(message_type),
            "message_content": str(message_content),
            "created_at": timestamp,
        }

        customer_messages[message_id] = new_message

        return json.dumps({
            "success": True,
            "customer_message": {
                "message_id": str(new_message["message_id"]),
                "ticket_id": str(new_message["ticket_id"]),
                "ticket_number": str(ticket_number),
                "customer_id": str(new_message["customer_id"]),
                "customer_email": str(customer_email),
                "message_type": str(new_message["message_type"]),
                "message_content": str(new_message["message_content"]),
                "created_at": str(new_message["created_at"]),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "send_customer_message",
                "description": "Sends an update message to a customer for an existing ticket. It should be used when you need to communicate a status update or information to a customer.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_number": {
                            "type": "string",
                            "description": "The number of the ticket",
                        },
                        "customer_email": {
                            "type": "string",
                            "description": "The email of the customer",
                        },
                        "message_type": {
                            "type": "string",
                            "description": "The type of the customer message",
                            "enum": ["investigating", "root_cause_identified", "fix_in_progress", "awaiting_external", "resolved"],
                        },
                        "message_content": {
                            "type": "string",
                            "description": "The content of the message to send",
                        },
                    },
                    "required": ["ticket_number", "customer_email", "message_type", "message_content"],
                },
            },
        }
