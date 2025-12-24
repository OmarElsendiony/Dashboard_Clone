import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class SetNotificationMute(Tool):
    """
    Set notification mute/unmute behavior for a user with time-based restrictions.
    Configures when notifications should be muted for a specific user.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_email: str,
        mute_enabled: bool,
        start_time: str,
        end_time: str,
    ) -> str:
        """
        Sets notification mute settings for a user with time-based restrictions.
        
        Args:
            data: The complete data dictionary containing all tables
            user_email: Email address of the user (required)
            mute_enabled: Whether notification muting is enabled (required)
            start_time: Start time for mute period in HH:MM format (required)
            end_time: End time for mute period in HH:MM format (required)
            
        Returns:
            JSON string with success status and mute settings or error message
        """

        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            try:
                max_id = max(int(k) for k in table.keys() if k.isdigit())
                return str(max_id + 1)
            except ValueError:
                return "1"

        def validate_time_format(time_str: str) -> bool:
            """Validates time format is HH:MM"""
            try:
                parts = time_str.split(":")
                if len(parts) != 2:
                    return False
                hours = int(parts[0])
                minutes = int(parts[1])
                return 0 <= hours <= 23 and 0 <= minutes <= 59
            except (ValueError, AttributeError):
                return False

        # Fixed timestamp as per requirements
        timestamp = "2025-12-12T12:00:00"

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        users = data.get("users", {})
        
        if not isinstance(users, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid users container: expected dict at data['users']",
                }
            )

        # Validate required parameters
        if not user_email:
            return json.dumps(
                {"success": False, "error": "user_email is required"}
            )

        if mute_enabled is None or mute_enabled == "":
            return json.dumps(
                {"success": False, "error": "mute_enabled is required"}
            )

        # Convert mute_enabled to boolean if it's a string
        if isinstance(mute_enabled, str):
            if mute_enabled.lower() in ["true", "1", "yes"]:
                mute_enabled = True
            elif mute_enabled.lower() in ["false", "0", "no"]:
                mute_enabled = False
            else:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid mute_enabled value: '{mute_enabled}'. Must be true/false, 1/0, or yes/no",
                    }
                )
        elif not isinstance(mute_enabled, bool):
            return json.dumps(
                {"success": False, "error": "mute_enabled must be a boolean or boolean string"}
            )

        if not start_time:
            return json.dumps(
                {"success": False, "error": "start_time is required"}
            )

        if not end_time:
            return json.dumps(
                {"success": False, "error": "end_time is required"}
            )

        # Validate time formats
        if not validate_time_format(start_time):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid start_time format: '{start_time}'. Must be in HH:MM format (e.g., '22:00')",
                }
            )

        if not validate_time_format(end_time):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid end_time format: '{end_time}'. Must be in HH:MM format (e.g., '07:00')",
                }
            )

        # Find user by email
        user_id = None
        user_email_str = str(user_email)
        
        for uid, user_data in users.items():
            if isinstance(user_data, dict) and user_data.get("email") == user_email_str:
                user_id = uid
                break
        
        if not user_id:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with email '{user_email}' not found",
                }
            )

        # Initialize notification_mute_settings if not exists
        if "notification_mute_settings" not in data:
            data["notification_mute_settings"] = {}
        
        notification_mute_settings = data["notification_mute_settings"]

        # Check if user already has a mute setting and update it, or create new one
        existing_setting_id = None
        for setting_id, setting in notification_mute_settings.items():
            if isinstance(setting, dict) and setting.get("user_id") == user_id:
                existing_setting_id = setting_id
                break

        if existing_setting_id:
            # Update existing setting
            notification_mute_settings[existing_setting_id].update({
                "mute_enabled": mute_enabled,
                "start_time": start_time,
                "end_time": end_time,
                "updated_at": timestamp,
            })
            mute_setting = notification_mute_settings[existing_setting_id]
            action = "updated"
        else:
            # Create new setting
            new_setting_id = generate_id(notification_mute_settings)
            
            new_mute_setting = {
                "setting_id": new_setting_id,
                "user_id": user_id,
                "mute_enabled": mute_enabled,
                "start_time": start_time,
                "end_time": end_time,
                "created_at": timestamp,
                "updated_at": timestamp,
            }

            notification_mute_settings[new_setting_id] = new_mute_setting
            mute_setting = new_mute_setting
            action = "created"

        # Apply mute/unmute to user's notifications
        notifications = data.get("notifications", {})
        affected_notifications = []
        
        for notif_id, notification in notifications.items():
            if isinstance(notification, dict) and notification.get("user_id") == user_id:
                # Update the muted status based on mute_enabled setting
                notification["muted"] = mute_enabled
                affected_notifications.append({
                    "notification_id": notification["notification_id"],
                    "title": notification["title"],
                    "notification_type": notification["notification_type"],
                    "muted": notification["muted"],
                    "status": notification["status"]
                })

        return json.dumps({
            "success": True, 
            "mute_setting": mute_setting, 
            "action": action,
            "affected_notifications": affected_notifications,
            "notifications_count": len(affected_notifications)
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "set_notification_mute",
                "description": (
                    "Set notification mute/unmute behavior for a user with time-based restrictions. "
                    "Configures when notifications should be muted for a specific user. "
                    "The mute period is defined by start_time and end_time in HH:MM format. "
                    "When mute_enabled is true, notifications during the specified time window will be muted."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_email": {
                            "type": "string",
                            "description": "Email address of the user (required).",
                        },
                        "mute_enabled": {
                            "type": "boolean",
                            "description": "Whether notification muting is enabled (required).",
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Start time for mute period in HH:MM format, e.g., '22:00' (required).",
                        },
                        "end_time": {
                            "type": "string",
                            "description": "End time for mute period in HH:MM format, e.g., '07:00' (required).",
                        },
                    },
                    "required": ["user_email", "mute_enabled", "start_time", "end_time"],
                },
            },
        }

