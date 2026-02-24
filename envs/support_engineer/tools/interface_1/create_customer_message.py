import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreateCustomerMessage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        customer_id: str,
        message_type: str,
        message_content: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        if not ticket_id:
            return json.dumps({
                "success": False,
                "error": "Missing required argument: 'ticket_id' is required."
            })

        if not customer_id:
            return json.dumps({
                "success": False,
                "error": "Missing required argument: 'customer_id' is required."
            })

        if not message_type:
            return json.dumps({
                "success": False,
                "error": "Missing required argument: 'message_type' is required."
            })

        if not message_content:
            return json.dumps({
                "success": False,
                "error": "Missing required argument: 'message_content' is required."
            })

        ticket_id = str(ticket_id).strip()
        customer_id = str(customer_id).strip()
        message_type = str(message_type).strip()
        message_content = str(message_content)

        tickets = data.get("tickets", {})
        if not isinstance(tickets, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'tickets' must be a dictionary"
            })

        customers = data.get("customers", {})
        if not isinstance(customers, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'customers' must be a dictionary"
            })

        customer_messages = data.get("customer_messages", {})
        if not isinstance(customer_messages, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'customer_messages' must be a dictionary"
            })

        ticket_exists = False
        for k, v in tickets.items():
            if isinstance(v, dict) and str(v.get("ticket_id", "")).strip() == ticket_id:
                ticket_exists = True
                break

        if not ticket_exists:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: ticket_id '{ticket_id}' not found."
            })

        customer_exists = False
        for k, v in customers.items():
            if isinstance(v, dict) and str(v.get("customer_id", "")).strip() == customer_id:
                customer_exists = True
                break

        if not customer_exists:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: customer_id '{customer_id}' not found."
            })

        max_id = 0
        for k in customer_messages.keys():
            try:
                num = int(str(k))
                if num > max_id:
                    max_id = num
            except ValueError:
                continue

        for v in customer_messages.values():
            if isinstance(v, dict):
                try:
                    num = int(str(v.get("message_id", "0")))
                    if num > max_id:
                        max_id = num
                except ValueError:
                    continue

        new_message_id = str(max_id + 1)
        timestamp = "2026-02-02 23:59:00"

        new_message = {
            "message_id": new_message_id,
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "message_type": message_type,
            "message_content": message_content,
            "created_at": timestamp
        }

        customer_messages[new_message_id] = new_message

        return json.dumps({
            "success": True,
            "message_record": new_message,
            "message": f"Customer message '{new_message_id}' created successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_customer_message",
                "description": (
                    "Creates a new message record in the customer_messages table, linking it to a specific ticket and customer.\n"
                    " Purpose: Facilitates the saving of draft messages directed to customers. Specifically used to fulfill the 'Draft Constraint' requirement in the policy.\n"
                    " When to use: Use this tool for ONE distinct step: 'Select Tone (AER)'. You use this specifically to fulfill the 'Draft Constraint' requirement, which dictates that you must save a message with the exact message_type as 'fix_in_progress' and hold it until the content passes the Validate Draft before sending step.\n"
                    " Returns: Returns a JSON string containing a success boolean, the newly created message dictionary object, and a success message text. Fails if the ticket_id or customer_id do not exist."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The unique identifier of the ticket this message relates to."
                        },
                        "customer_id": {
                            "type": "string",
                            "description": "The unique identifier of the customer receiving or associated with this message."
                        },
                        "message_type": {
                            "type": "string",
                            "description": "The classification of the message (e.g., 'fix_in_progress')."
                        },
                        "message_content": {
                            "type": "string",
                            "description": "The actual text body of the drafted message."
                        }
                    },
                    "required": ["ticket_id", "customer_id", "message_type", "message_content"]
                }
            }
        }
