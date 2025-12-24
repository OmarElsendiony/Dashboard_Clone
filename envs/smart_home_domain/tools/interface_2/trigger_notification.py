import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class TriggerNotification(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: str,
        home_id: str,
        notification_type: str,
        title: str,
        message: str,
        muted: bool,
        related_device_id: str,
        status: Optional[str] = None
    ) -> str:
        """
        Create a new notification for a user.
        """
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        notifications_dict = data.get("notifications", {})
        if not isinstance(notifications_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid notifications container: expected dict at data['notifications']"
            })

        users_dict = data.get("users", {})
        if not isinstance(users_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid users container: expected dict at data['users']"
            })

        homes_dict = data.get("homes", {})
        if not isinstance(homes_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid homes container: expected dict at data['homes']"
            })

        devices_dict = data.get("devices", {})
        if not isinstance(devices_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid devices container: expected dict at data['devices']"
            })

        # Validate required parameters
        if not user_id:
            return json.dumps({
                "success": False,
                "error": "user_id is required"
            })

        if not home_id:
            return json.dumps({
                "success": False,
                "error": "home_id is required"
            })

        if not notification_type:
            return json.dumps({
                "success": False,
                "error": "notification_type is required"
            })

        if not title:
            return json.dumps({
                "success": False,
                "error": "title is required"
            })

        if not message:
            return json.dumps({
                "success": False,
                "error": "message is required"
            })

        user_id_str = str(user_id).strip()
        home_id_str = str(home_id).strip()
        notification_type_str = str(notification_type).strip().lower()
        title_str = str(title).strip()
        message_str = str(message).strip()

        # Validate muted is a boolean or string "true"/"false"
        if isinstance(muted, bool):
            muted_bool = muted
        elif isinstance(muted, str):
            muted_str = muted.strip().lower()
            if muted_str == "true":
                muted_bool = True
            elif muted_str == "false":
                muted_bool = False
            else:
                return json.dumps({
                    "success": False,
                    "error": "muted must be a boolean value "
                })
        else:
            return json.dumps({
                "success": False,
                "error": "muted must be a boolean value "
            })

        # Validate notification_type
        if notification_type_str not in ["alert", "energy_summary"]:
            return json.dumps({
                "success": False,
                "error": "notification_type must be 'alert' or 'energy_summary'"
            })

        # Validate user exists
        if user_id_str not in users_dict:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{user_id_str}' not found"
            })

        # Validate home exists
        if home_id_str not in homes_dict:
            return json.dumps({
                "success": False,
                "error": f"Home with ID '{home_id_str}' not found"
            })

        # Validate related_device_id if provided
        related_device_id_clean = None
        if related_device_id:
            related_device_id_str = str(related_device_id).strip()
            if related_device_id_str and related_device_id_str.lower() != "null":
                related_device_id_clean = related_device_id_str
                if related_device_id_clean not in devices_dict:
                    return json.dumps({
                        "success": False,
                        "error": f"Device with ID '{related_device_id_clean}' not found"
                    })

        # Validate status if provided
        notification_status = "pending"
        if status:
            status_str = str(status).strip().lower()
            if status_str not in ["pending", "sent", "failed", "read"]:
                return json.dumps({
                    "success": False,
                    "error": "status must be one of: 'pending', 'sent', 'failed', 'read'"
                })
            notification_status = status_str

        # Generate new notification_id
        numeric_ids = []
        for key in notifications_dict.keys():
            try:
                numeric_ids.append(int(key))
            except (TypeError, ValueError):
                continue
        new_notification_id = str(max(numeric_ids, default=0) + 1)

        timestamp = "2025-12-19T23:59:00"

        # Create new notification record
        new_notification = {
            "notification_id": new_notification_id,
            "user_id": user_id_str,
            "home_id": home_id_str,
            "notification_type": notification_type_str,
            "title": title_str,
            "message": message_str,
            "muted": muted_bool,
            "related_device_id": related_device_id_clean,
            "status": notification_status,
            "created_at": timestamp
        }

        # Add to data
        notifications_dict[new_notification_id] = new_notification

        return json.dumps({
            "success": True,
            "notification": new_notification
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "trigger_notification",
                "description": "Create a new notification for a user. Validates that the user, home, and device (if provided) exist. Notification type must be 'alert' or 'energy_summary'. Status defaults to 'pending' if not provided. Returns the created notification with generated notification_id.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user receiving the notification."
                        },
                        "home_id": {
                            "type": "string",
                            "description": "The ID of the home associated with the notification."
                        },
                        "notification_type": {
                            "type": "string",
                            "description": "The type of notification: 'alert' or 'energy_summary'."
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the notification."
                        },
                        "message": {
                            "type": "string",
                            "description": "The message content of the notification."
                        },
                        "muted": {
                            "type": "boolean",
                            "description": "Whether the notification is muted."
                        },
                        "related_device_id": {
                            "type": "string",
                            "description": "The ID of the device related to the notification, if any."
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional status: 'pending', 'sent', 'failed', or 'read'. Defaults to 'pending'."
                        }
                    },
                    "required": ["user_id", "home_id", "notification_type", "title", "message", "muted", "related_device_id"]
                }
            }
        }
