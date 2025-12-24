import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateNotification(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        notification_type: str,
        title: str,
        message: str,
        delivery_method: Optional[str] = None,
        accessory_id: Optional[str] = None,
        muted: Optional[bool] = False,
    ) -> str:
        """
        Create a reusable notification template for a home.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        users = data.get("users")
        homes = data.get("homes")
        devices = data.get("devices")
        notifications = data.get("notifications")

        if not isinstance(users, dict):
            return json.dumps({"success": False, "error": "users store missing"})
        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(notifications, dict):
            return json.dumps({"success": False, "error": "notifications store missing"})

        if not isinstance(home_name, str) or not home_name.strip():
            return json.dumps({"success": False, "error": "home_name must be provided"})
        home_name = home_name.strip()

        # Find home by name
        home_id = None
        home = None
        for hid, h in homes.items():
            if h.get("home_name", "").strip().lower() == home_name.lower():
                home_id = hid
                home = h
                break
        if not home_id:
            return json.dumps({"success": False, "error": f"Home '{home_name}' not found"})

        # Per schema, notifications require a user_id; use the home owner as the template owner
        owner_id = home.get("owner_id")
        if owner_id not in users:
            return json.dumps({"success": False, "error": f"Owner for home '{home_name}' not found"})

        if not isinstance(notification_type, str) or not notification_type.strip():
            return json.dumps({"success": False, "error": "notification_type must be provided"})
        notification_type = notification_type.strip().lower()

        allowed_types = {"alert", "device_status", "energy_summary"}
        if notification_type not in allowed_types:
            return json.dumps({"success": False, "error": f"notification_type must be one of {', '.join(allowed_types)}"})

        if not isinstance(title, str) or not title.strip():
            return json.dumps({"success": False, "error": "title must be provided"})
        title = title.strip()

        if not isinstance(message, str) or not message.strip():
            return json.dumps({"success": False, "error": "message must be provided"})
        message = message.strip()

        device_val = None
        if accessory_id:
            if not isinstance(devices, dict):
                return json.dumps({"success": False, "error": "devices store missing"})
            if not isinstance(accessory_id, str) or not accessory_id.strip():
                return json.dumps({"success": False, "error": "accessory_id must be a non-empty string"})
            device_val = accessory_id.strip()
            if device_val not in devices:
                return json.dumps({"success": False, "error": f"Accessory '{device_val}' not found"})
            if devices[device_val].get("home_id") != home_id:
                return json.dumps({"success": False, "error": f"Accessory '{device_val}' does not belong to home '{home_name}'"})

        muted_val = bool(muted)

        notification_id = generate_id(notifications)
        timestamp = "2025-12-19T23:59:00"

        record = {
            "notification_id": notification_id,
            "user_id": owner_id,
            "home_id": home_id,
            "notification_type": notification_type,
            "title": title,
            "message": message,
            "muted": muted_val,
            "related_device_id": device_val,
            "delivery_method": delivery_method.strip() if isinstance(delivery_method, str) and delivery_method.strip() else None,
            "status": "pending",
            "sent_at": None,
            "read_at": None,
            "created_at": timestamp,
        }

        notifications[notification_id] = record

        return json.dumps({
            "success": True,
            "notification": {
                "home_name": home_name,
                "notification_id": record.get("notification_id"),
                "notification_type": record.get("notification_type"),
                "title": record.get("title"),
                "message": record.get("message"),
                "delivery_method": record.get("delivery_method"),
                "accessory_id": record.get("related_device_id"),
                "muted": record.get("muted"),
                "status": record.get("status"),
                "sent_at": record.get("sent_at"),
                "read_at": record.get("read_at"),
                "created_at": record.get("created_at"),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_notification",
                "description": "Create a notification template for a home.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "notification_type": {
                            "type": "string",
                            "description": "Type of notification; allowed values: alert, device_status, energy_summary.",
                        },
                        "title": {
                            "type": "string",
                            "description": "Title of the notification.",
                        },
                        "message": {
                            "type": "string",
                            "description": "Message content of the notification.",
                        },
                        "delivery_method": {
                            "type": "string",
                            "description": "Optional delivery method (e.g., push, email, sms, in_app).",
                        },
                        "accessory_id": {
                            "type": "string",
                            "description": "Optional related accessory identifier.",
                        },
                        "muted": {
                            "type": "boolean",
                            "description": "Whether the notification is muted (True/False).",
                        },
                    },
                    "required": ["home_name", "notification_type", "title", "message"],
                },
            },
        }

