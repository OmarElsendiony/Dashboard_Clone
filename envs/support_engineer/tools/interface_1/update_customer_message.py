import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateCustomerMessage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        message_id: str,
        new_message_type: Optional[str] = None,
        new_message_content: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        if not message_id:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'message_id' is required."
            })

        message_id = str(message_id).strip()
        customer_messages = data.get("customer_messages", {})

        if not isinstance(customer_messages, dict):
            return json.dumps({
                "success": False,
                "error": "Internal data structure error: missing 'customer_messages' table."
            })

        if message_id not in customer_messages:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: message_id '{message_id}' not found."
            })

        if new_message_type is None and new_message_content is None:
            return json.dumps({
                "success": False,
                "error": "No update parameters provided. Provide at least new_message_type or new_message_content."
            })

        target_message = customer_messages[message_id]
        has_changes = False

        if new_message_type is not None:
            new_type_str = str(new_message_type).strip()
            if target_message.get("message_type") != new_type_str:
                target_message["message_type"] = new_type_str
                has_changes = True

        if new_message_content is not None:
            new_content_str = str(new_message_content).strip()
            if target_message.get("message_content") != new_content_str:
                target_message["message_content"] = new_content_str
                has_changes = True

        if not has_changes:
            return json.dumps({
                "success": True,
                "message": target_message,
                "info": "No changes detected. The provided values are identical to the existing record (idempotent)."
            })

        return json.dumps({
            "success": True,
            "message": target_message,
            "info": f"Customer message '{message_id}' successfully updated."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_customer_message",
                "description": (
                    "Updates the content or type of an existing customer message record.\n"
                    " Purpose: Allows post-send corrections to messages. Includes idempotency checks to prevent redundant writes if the new values match the existing values.\n"
                    " When to use: Use this tool if a previously sent message requires a critical correction to its text or type category.\n"
                    " Returns: A JSON string containing a success boolean, the updated message dictionary object, and a confirmation text. Returns an idempotent success if no actual changes were made."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message_id": {
                            "type": "string",
                            "description": "The unique identifier of the customer message to update."
                        },
                        "new_message_type": {
                            "type": "string",
                            "description": "The new category/type of the message. Optional."
                        },
                        "new_message_content": {
                            "type": "string",
                            "description": "The corrected text content of the message. Optional."
                        }
                    },
                    "required": ["message_id"]
                }
            }
        }
