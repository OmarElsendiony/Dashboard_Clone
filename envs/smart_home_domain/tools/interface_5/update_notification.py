import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class UpdateNotification(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        notification_id: str,
        title: Optional[str] = None,
        message: Optional[str] = None,
        status: Optional[str] = None,
        muted: Optional[bool] = None,
    ) -> str:
        """
        Update notification template details.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        notifications = data.get("notifications")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(notifications, dict):
            return json.dumps({"success": False, "error": "notifications store missing"})

        if not isinstance(home_name, str) or not home_name.strip():
            return json.dumps({"success": False, "error": "home_name must be provided"})
        home_name = home_name.strip()

        # Find home by name
        home_id = None
        for hid, home in homes.items():
            if home.get("home_name", "").strip().lower() == home_name.lower():
                home_id = hid
                break
        if not home_id:
            return json.dumps({"success": False, "error": f"Home '{home_name}' not found"})

        if not isinstance(notification_id, str) or not notification_id.strip():
            return json.dumps({"success": False, "error": "notification_id must be provided"})
        notification_id = notification_id.strip()

        if notification_id not in notifications:
            return json.dumps({"success": False, "error": f"Notification '{notification_id}' not found"})

        notification = notifications[notification_id]
        if notification.get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Notification '{notification_id}' does not belong to home '{home_name}'"})
        updates = False

        if title is not None:
            if not isinstance(title, str) or not title.strip():
                return json.dumps({"success": False, "error": "title must be a non-empty string"})
            notification["title"] = title.strip()
            updates = True

        if message is not None:
            if not isinstance(message, str) or not message.strip():
                return json.dumps({"success": False, "error": "message must be a non-empty string"})
            notification["message"] = message.strip()
            updates = True

        if status is not None:
            if not isinstance(status, str):
                return json.dumps({"success": False, "error": "status must be a string"})
            status_val = status.strip().lower()
            if status_val not in {"pending", "sent", "failed", "read"}:
                return json.dumps({"success": False, "error": "status must be one of pending, sent, failed, read"})
            notification["status"] = status_val
            updates = True

        if muted is not None:
            notification["muted"] = bool(muted)
            updates = True

        if not updates:
            return json.dumps({"success": False, "error": "No updates provided"})

        return json.dumps({
            "success": True,
            "notification": {
                "home_name": home_name,
                "notification_id": notification.get("notification_id"),
                "notification_type": notification.get("notification_type"),
                "title": notification.get("title"),
                "message": notification.get("message"),
                "delivery_method": notification.get("delivery_method"),
                "accessory_id": notification.get("related_device_id"),
                "muted": notification.get("muted"),
                "status": notification.get("status"),
                "sent_at": notification.get("sent_at"),
                "read_at": notification.get("read_at"),
                "created_at": notification.get("created_at"),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_notification",
                "description": "Update notification details including title, message, muted status, and current status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "notification_id": {
                            "type": "string",
                            "description": "Identifier of the notification to update.",
                        },
                        "title": {
                            "type": "string",
                            "description": "Optional new title.",
                        },
                        "message": {
                            "type": "string",
                            "description": "Optional new message.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional new status; allowed values: pending, sent, failed, read.",
                        },
                        "muted": {
                            "type": "boolean",
                            "description": "Optional muted setting (True/False).",
                        },
                    },
                    "required": ["home_name", "notification_id"],
                },
            },
        }

