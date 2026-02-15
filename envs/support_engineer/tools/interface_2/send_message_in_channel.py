import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class SendMessageInChannel(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: str,
        sender_id: str,
        message: str,
        thread_id: Optional[str] = None,
        related_ticket_id: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-02 23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        if not channel_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'channel_id'"})

        if not sender_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'sender_id'"})

        if not message:
            return json.dumps({"success": False, "error": "Missing required parameter: 'message'"})

        channels_dict = data.get("channels", {})
        channel_messages_dict = data.get("channel_messages", {})
        threads_dict = data.get("threads", {})
        users_dict = data.get("users", {})
        tickets_dict = data.get("tickets", {})

        channel_id_str = str(channel_id).strip()
        sender_id_str = str(sender_id).strip()
        message_str = str(message).strip()
        thread_id_str = str(thread_id).strip() if thread_id else None
        related_ticket_id_str = (
            str(related_ticket_id).strip() if related_ticket_id else None
        )

        if not message_str:
            return json.dumps({"success": False, "error": "Message cannot be empty"})

        if channel_id_str not in channels_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Channel with ID '{channel_id_str}' not found",
                }
            )

        channel = channels_dict[channel_id_str]

        if not isinstance(channel, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid channel data structure for channel ID '{channel_id_str}'",
                }
            )

        channel_status = str(channel.get("status", "")).strip()
        if channel_status != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Cannot send message to channel '{channel_id_str}' with status '{channel_status}'. Channel must be active.",
                }
            )

        if sender_id_str not in users_dict:
            return json.dumps(
                {"success": False, "error": f"User with ID '{sender_id_str}' not found"}
            )

        sender = users_dict[sender_id_str]

        if not isinstance(sender, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid user data structure for sender ID '{sender_id_str}'",
                }
            )

        sender_status = sender.get("status")
        if sender_status != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"User '{sender_id_str}' is not active and cannot send messages",
                }
            )

        if thread_id_str:
            if thread_id_str not in threads_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Thread with ID '{thread_id_str}' not found",
                    }
                )

            thread = threads_dict[thread_id_str]

            if not isinstance(thread, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid thread data structure for thread ID '{thread_id_str}'",
                    }
                )

            thread_channel_id = str(thread.get("channel_id", "")).strip()
            if thread_channel_id != channel_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Thread '{thread_id_str}' does not belong to channel '{channel_id_str}'",
                    }
                )

            thread_status = str(thread.get("status", "")).strip()
            if thread_status != "active":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Cannot send message to thread '{thread_id_str}' with status '{thread_status}'. Thread must be active.",
                    }
                )

        if related_ticket_id_str:
            if related_ticket_id_str not in tickets_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Related ticket with ID '{related_ticket_id_str}' not found",
                    }
                )

            ticket = tickets_dict[related_ticket_id_str]

            if not isinstance(ticket, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid ticket data structure for ticket ID '{related_ticket_id_str}'",
                    }
                )

        new_message_id = generate_id(channel_messages_dict)

        new_message = {
            "message_id": new_message_id,
            "channel_id": channel_id_str,
            "thread_id": thread_id_str,
            "sender_id": sender_id_str,
            "message": message_str,
            "related_ticket_id": related_ticket_id_str,
            "sent_at": timestamp,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        channel_messages_dict[new_message_id] = new_message

        message_return = new_message.copy()
        message_return["sender_email"] = sender.get("email")
        message_return["sender_name"] = (
            f"{sender.get('first_name', '')} {sender.get('last_name', '')}".strip()
        )
        message_return["channel_name"] = channel.get("name")
        message_return["channel_type"] = channel.get("channel_type")

        if thread_id_str and thread_id_str in threads_dict:
            thread = threads_dict[thread_id_str]
            if isinstance(thread, dict):
                message_return["thread_name"] = thread.get("thread_name")

        if related_ticket_id_str and related_ticket_id_str in tickets_dict:
            ticket = tickets_dict[related_ticket_id_str]
            if isinstance(ticket, dict):
                message_return["ticket_number"] = ticket.get("ticket_number")

        # Build success message
        destination = f"channel '{channel.get('name', channel_id_str)}'"
        if thread_id_str:
            thread_name = threads_dict.get(thread_id_str, {}).get(
                "thread_name", thread_id_str
            )
            destination += f" in thread '{thread_name}'"

        success_message = f"Message sent successfully to {destination}"

        return json.dumps(
            {
                "success": True,
                "message": message_return,
                "message_text": success_message,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "send_message_in_channel",
                "description": (
                    "Sends a message to a communication channel, optionally within a specific thread. "
                    "This function posts notifications, updates, or coordination messages to team channels. "
                    "Use this to broadcast incident updates to major incidents channels, "
                    "notify teams about ticket status changes, request assistance or escalations, "
                    "post security alerts to security operations channels, coordinate investigation activities, "
                    "share resolution updates with stakeholders, flag SLA breaches or violations, "
                    "or communicate with internal teams about customer issues. "
                    "Messages can be posted to channel-wide discussions or focused within specific threads for organized conversation."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "The unique identifier of the channel where the message will be sent.",
                        },
                        "sender_id": {
                            "type": "string",
                            "description": "The unique identifier of the user sending the message.",
                        },
                        "message": {
                            "type": "string",
                            "description": "The content of the message to send.",
                        },
                        "thread_id": {
                            "type": "string",
                            "description": "Optional. The unique identifier of the thread within the channel to post to.",
                        },
                        "related_ticket_id": {
                            "type": "string",
                            "description": "Optional. The unique identifier of the ticket this message relates to for context and traceability.",
                        },
                    },
                    "required": ["channel_id", "sender_id", "message"],
                },
            },
        }
