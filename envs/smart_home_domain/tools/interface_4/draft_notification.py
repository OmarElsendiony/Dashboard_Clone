import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class DraftNotification(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        muted: bool = False,
        household_id: Optional[str] = None,        
        device_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        users_dict = data.get("users", {})
        if not isinstance(users_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid users container: expected dict at data['users']",
                }
            )

        homes_dict = data.get("homes", {})
        if not isinstance(homes_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid homes container: expected dict at data['homes']",
                }
            )

        devices_dict = data.get("devices", {})
        if not isinstance(devices_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid devices container: expected dict at data['devices']",
                }
            )

        notifications_dict = data.get("notifications", {})
        if not isinstance(notifications_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid notifications container: expected dict at data['notifications']",
                }
            )

        # Type cast required parameters to string as requested
        if not user_id:
            return json.dumps({"success": False, "error": "user_id is required"})

        if not notification_type:
            return json.dumps(
                {"success": False, "error": "notification_type is required"}
            )

        if not title:
            return json.dumps({"success": False, "error": "title is required"})

        if not message:
            return json.dumps({"success": False, "error": "message is required"})

        user_id_str = str(user_id).strip()    
        notification_type_str = str(notification_type).strip()        
        title_str = str(title).strip()
        message_str = str(message).strip()
        home_id_str = str(household_id).strip() if household_id else None        

        # Validate user exists
        if user_id_str not in users_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with ID '{user_id_str}' not found",
                }
            )

        # Validate home exists
        if home_id_str and home_id_str not in homes_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Home with ID '{home_id_str}' not found",
                }
            )

        # Validate notification_type
        valid_notification_types = ["alert", "device_status", "energy_summary"]
        if notification_type_str not in valid_notification_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid notification_type '{notification_type_str}'. Must be one of: {', '.join(valid_notification_types)}",
                }
            )

        # Validate muted is boolean
        if not isinstance(muted, bool):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid muted parameter: must be a boolean value (True/False)",
                }
            )

        # Validate title length (max 255 characters)
        if len(title_str) > 255:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Title exceeds maximum length of 255 characters (current: {len(title_str)})",
                }
            )

        # Validate message length (max 1000 characters)
        if len(message_str) > 1000:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Message exceeds maximum length of 1000 characters (current: {len(message_str)})",
                }
            )

        # Validate device_id if provided
        device_id_str = None
        if device_id:
            device_id_str = str(device_id).strip()
            if device_id_str not in devices_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Device with ID '{device_id_str}' not found",
                    }
                )

        # Validate status if provided, otherwise default to 'pending'
        valid_statuses = ["pending", "sent", "failed", "read"]
        status_str = "pending"  # default value
        if status:
            status_str = str(status).strip()
            if status_str not in valid_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid status '{status_str}'. Must be one of: {', '.join(valid_statuses)}",
                    }
                )

        # Generate unique notification_id
        # Generate new IDs
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        notification_id = generate_id(notifications_dict)
        # Create timestamp
        created_at = "2025-12-19T23:59:00"

        # Create new notification entry
        new_notification = {
            "notification_id": notification_id,
            "user_id": user_id_str,
            "home_id": home_id_str,
            "notification_type": notification_type_str,
            "title": title_str,
            "message": message_str,
            "muted": muted,
            "related_device_id": device_id_str,
            "status": status_str,
            "sent_at": None,
            "read_at": None,
            "created_at": created_at,
        }

        # Add to data structure
        notifications_dict[notification_id] = new_notification

        new_notification_return = new_notification.copy()
        new_notification_return["household_id"] = new_notification_return.pop("home_id")

        return json.dumps(
            {
                "success": True,
                "notification_id": notification_id,
                "message": f"Notification '{title_str}' created successfully for user '{user_id_str}'",
                "notification": new_notification_return,                
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "draft_notification",
                "description": (
                    "Create a draft notification for a user. "
                    "Creates a notification with specified type, title, and message. "
                    "The notification can be linked to a specific device and can be muted. "
                    "Validates that the user exist. "
                    "If household_id is provided, validates that the household exists. "
                    "If device_id is provided, validates that the device exists. "
                    "Title must not exceed 255 characters. "
                    "Message must not exceed 1000 characters. "
                    "Notification types: 'alert', 'device_status', 'energy_summary'. "
                    "Status values: 'pending', 'sent', 'failed', 'read' (defaults to 'pending'). "
                    "Returns the created notification_id on success."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user who will receive the notification.",
                        },
                        "household_id": {
                            "type": "string",
                            "description": "Optional. The ID of the home/household associated with the notification.",
                        },
                        "notification_type": {
                            "type": "string",
                            "description": "The type of notification. Accepted values: 'alert', 'device_status', 'energy_summary'.",
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the notification (max 255 characters).",
                        },
                        "message": {
                            "type": "string",
                            "description": "The message content of the notification (max 1000 characters).",
                        },
                        "muted": {
                            "type": "boolean",
                            "description": "Default False. Whether the notification should be muted (True) or not (False).",
                        },
                        "device_id": {
                            "type": "string",
                            "description": "Optional. The ID of the device related to this notification.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional. The status of the notification. Accepted values: 'pending', 'sent', 'failed', 'read'. Defaults to 'pending'.",
                        },
                    },
                    "required": [
                        "user_id",
                        "notification_type",
                        "title",
                        "message",
                    ],
                },
            },
        }