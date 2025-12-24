import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class SendNotification(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        recipient: str,
        notification_type: str,
        notification_object: Dict[str, Any],
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        users = data.get("users", {})
        notifications = data.get("notifications", {})

        def generate_id(table: Dict[str, Any]) -> int:
            return max([int(k) for k in table.keys()], default=0) + 1

        next_notification_id = generate_id(notifications)
        if notification_type not in ["alert", "energy_summary", "device_status"]:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid notification type '{notification_type}'",
                }
            )

        if recipient:
            user = users.get(str(recipient))
            print(recipient)
            if not user:
                return json.dumps(
                    {"success": False, "error": f"User with id '{recipient}' not found"}
                )

        if not notification_object.get("title") or not notification_object.get(
            "message"
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": "Notification object must contain 'title' and 'message'",
                }
            )

        timestamp = "2025-12-19T23:59:00"
        # Create notification record
        notification_record = {
            "notification_id": str(next_notification_id),
            "user_id": recipient,
            "notification_type": notification_type,
            "title": notification_object.get("title", ""),
            "message": notification_object.get("message", ""),
            "status": "pending",
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        notifications[next_notification_id] = notification_record
        return json.dumps(
            {
                "success": True,
                "message": "Notification sent successfully.",
                "notification": notification_record,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "send_notification",
                "description": "Send a notification.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipient": {
                            "type": "string",
                            "description": "The recipient of the notification (user ID).",
                        },
                        "notification_type": {
                            "type": "string",
                            "description": "The type of notification (e.g., 'alert', 'device_status', 'energy_summary').",
                        },
                        "notification_object": {
                            "type": "object",
                            "description": "The notification content. E.g. {'title': 'Alert', 'message': 'Temperature is too high.'}",
                        },
                    },
                    "required": [
                        "recipient",
                        "notification_type",
                        "notification_object",
                    ],
                },
            },
        }
