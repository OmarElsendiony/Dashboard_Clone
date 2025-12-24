import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ListNotifications(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        status: Optional[str] = None,
        notification_type: Optional[str] = None,
    ) -> str:
        """
        List notification templates for a home with optional filters.
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

        status_filter = None
        if status:
            if not isinstance(status, str):
                return json.dumps({"success": False, "error": "status must be a string"})
            status_filter = status.strip().lower()
            if status_filter not in {"pending", "sent", "failed", "read"}:
                return json.dumps({"success": False, "error": "status must be one of pending, sent, failed, read"})

        type_filter = None
        if notification_type:
            if not isinstance(notification_type, str):
                return json.dumps({"success": False, "error": "notification_type must be a string"})
            type_filter = notification_type.strip().lower()
            if type_filter not in {"alert", "device_status", "energy_summary"}:
                return json.dumps({"success": False, "error": "notification_type must be one of alert, device_status, energy_summary"})

        result_notifications = []
        for notification in notifications.values():
            if notification.get("home_id") == home_id:
                if status_filter and notification.get("status") != status_filter:
                    continue
                if type_filter and notification.get("notification_type") != type_filter:
                    continue
                result_notifications.append({
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
                })

        return json.dumps({"success": True, "notifications": result_notifications})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_notifications",
                "description": "List notifications for a home with optional filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional status filter; allowed values: pending, sent, failed, read.",
                        },
                        "notification_type": {
                            "type": "string",
                            "description": "Optional type filter; allowed values: alert, device_status, energy_summary.",
                        },
                    },
                    "required": ["home_name"],
                },
            },
        }

