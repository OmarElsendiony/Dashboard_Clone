import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ConstructNotification(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        related_device_id: Optional[str] = None,
        status: str = "pending",
        home_id: Optional[str] = None,
    ) -> str:
        """Create a notification record for a user/home combination."""
        try:
            if not isinstance(data, dict):
                return json.dumps(
                    {"success": False, "error": "Invalid payload: data must be dict."}
                )

            users = data.get("users")
            homes = data.get("homes")
            devices = data.get("devices")
            notifications = data.get("notifications")

            if not isinstance(users, dict) or not isinstance(homes, dict) or not isinstance(notifications, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Missing users, homes, or notifications collections in dataset.",
                    }
                )

            if not isinstance(user_id, str) or not user_id.strip():
                return json.dumps(
                    {"success": False, "error": "user_id is required to construct the notification."}
                )
            user_id_clean = user_id.strip()
            if user_id_clean not in users:
                return json.dumps({"success": False, "error": "User not found."})

            home_id_clean = None
            if home_id is not None:
                if not isinstance(home_id, str) or not home_id.strip():
                    return json.dumps(
                        {"success": False, "error": "home_id must be a non-empty string when provided."}
                    )
                home_id_clean = home_id.strip()
                if home_id_clean not in homes:
                    return json.dumps({"success": False, "error": "Home not found."})

            if not isinstance(notification_type, str) or not notification_type.strip():
                return json.dumps(
                    {"success": False, "error": "notification_type must be provided (e.g., alert, device_status, energy_summary)."}
                )
            notification_type_clean = notification_type.strip()

            if not isinstance(title, str) or not title.strip():
                return json.dumps({"success": False, "error": "title must be a non-empty string."})
            title_clean = title.strip()

            if not isinstance(message, str) or not message.strip():
                return json.dumps({"success": False, "error": "message must be a non-empty string."})
            message_clean = message.strip()

            status_clean = status.strip().lower() if isinstance(status, str) else ""
            allowed_statuses = {"pending", "sent", "read", "failed"}
            if status_clean not in allowed_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": "status must be one of pending, sent, read, or failed.",
                    }
                )

            device_id_clean = None
            if related_device_id is not None:
                if not isinstance(related_device_id, str) or not related_device_id.strip():
                    return json.dumps(
                        {"success": False, "error": "related_device_id must be a non-empty string when provided."}
                    )
                if home_id_clean is None:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "home_id is required when related_device_id is provided.",
                        }
                    )
                devices = devices or {}
                device_id_clean = related_device_id.strip()
                device_record = devices.get(device_id_clean)
                if not isinstance(device_record, dict):
                    return json.dumps({"success": False, "error": "related_device_id not found."})
                if str(device_record.get("home_id", "")).strip() != home_id_clean:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "related_device_id belongs to a different household.",
                        }
                    )

            timestamp = "2025-12-19T23:59:00"

            def _generate_numeric_id(container: Dict[str, Any]) -> str:
                numeric_ids = []
                for key in container.keys():
                    try:
                        numeric_ids.append(int(str(key)))
                    except ValueError:
                        continue
                next_id = max(numeric_ids) + 1 if numeric_ids else len(container) + 1
                return str(next_id)

            notification_id = _generate_numeric_id(notifications)
            sent_at_value: Optional[str] = None
            read_at_value: Optional[str] = None
            if status_clean in {"sent", "read"}:
                sent_at_value = timestamp
            if status_clean == "read":
                read_at_value = timestamp

            new_notification = {
                "notification_id": notification_id,
                "user_id": user_id_clean,
                "home_id": home_id_clean,
                "notification_type": notification_type_clean,
                "title": title_clean,
                "message": message_clean,
                "muted": False,
                "related_device_id": device_id_clean,
                "status": status_clean,
                "sent_at": sent_at_value,
                "read_at": read_at_value,
                "created_at": timestamp,
            }
            notifications[notification_id] = new_notification

            return json.dumps(
                {
                    "success": True,
                    "message": "Notification constructed successfully.",
                    "notification": new_notification,
                }
            )
        except Exception as exc:
            return json.dumps(
                {"success": False, "error": f"Failed to construct notification: {exc}"}
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "construct_notification",
                "description": (
                    "Create a notification entry for a user. Requires user_id, home_id, notification_type, title, and message."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User to whom the notification is addressed.",
                        },
                        "home_id": {
                            "type": "string",
                            "description": "Optional home context for the notification.",
                        },
                        "notification_type": {
                            "type": "string",
                            "description": "Notification category (e.g., alert, device_status, energy_summary).",
                        },
                        "title": {
                            "type": "string",
                            "description": "Notification title.",
                        },
                        "message": {
                            "type": "string",
                            "description": "Notification body text.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional status for the notification (pending, sent, read, failed). Defaults to pending.",
                        },
                        "related_device_id": {
                            "type": "string",
                            "description": "Optional device identifier related to the notification.",
                        },
                    },
                    "required": ["user_id", "notification_type", "title", "message"],
                },
            },
        }
