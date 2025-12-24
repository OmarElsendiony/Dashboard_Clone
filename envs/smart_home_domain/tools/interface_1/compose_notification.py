import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ComposeNotification(Tool):
    """
    Compose a notification configuration for a user.
    Creates a notification record in pending status that can be used in routines.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        recipient: str,
        title: str,
        message: str,
        notification_type: str = "alert",
    ) -> str:
        """
        Creates a notification configuration.
        
        Args:
            data: The complete data dictionary containing all tables
            recipient: User ID or email of the notification recipient (required)
            title: Title of the notification (required)
            message: Message content of the notification (required)
            notification_type: Type of notification - 'alert', 'device_status', or 'energy_summary' (default: 'alert')
            
        Returns:
            JSON string with success status and notification details or error message
        """

        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            try:
                max_id = max(int(k) for k in table.keys() if str(k).isdigit())
                return str(max_id + 1)
            except ValueError:
                return "1"

        # Fixed timestamp as per requirements
        timestamp = "2025-12-19T23:59:00"

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        notifications = data.get("notifications", {})
        users = data.get("users", {})

        if not isinstance(notifications, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid notifications container: expected dict at data['notifications']",
                }
            )

        if not isinstance(users, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid users container: expected dict at data['users']",
                }
            )

        # Validate required parameters
        if not recipient:
            return json.dumps(
                {"success": False, "error": "recipient is required"}
            )

        # Convert title and message to strings to handle integer inputs
        title = str(title) if title is not None else ""
        message = str(message) if message is not None else ""

        if not title or not title.strip():
            return json.dumps(
                {"success": False, "error": "title is required and cannot be empty"}
            )

        if not message or not message.strip():
            return json.dumps(
                {"success": False, "error": "message is required and cannot be empty"}
            )

        # Validate notification_type enum
        valid_notification_types = ["alert", "device_status", "energy_summary"]
        if notification_type not in valid_notification_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid notification_type: '{notification_type}'. Must be one of {valid_notification_types}",
                }
            )

        # Resolve recipient - can be user_id or email
        user_id = None
        recipient_str = str(recipient)
        
        # Check if recipient is a user_id
        if recipient_str in users:
            user_id = recipient_str
        else:
            # Check if recipient is an email
            for uid, user_data in users.items():
                if isinstance(user_data, dict) and user_data.get("email") == recipient_str:
                    user_id = uid
                    break
        
        if not user_id:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with ID or email '{recipient}' not found",
                }
            )


        # Validate title length (varchar(255))
        if len(title.strip()) > 255:
            return json.dumps(
                {
                    "success": False,
                    "error": "title exceeds maximum length of 255 characters",
                }
            )

        # Validate message length (varchar(1000))
        if len(message.strip()) > 1000:
            return json.dumps(
                {
                    "success": False,
                    "error": "message exceeds maximum length of 1000 characters",
                }
            )

        # Generate new notification ID
        new_notification_id = generate_id(notifications)

        # Create notification record with pending status
        # This is a pre-configured notification that hasn't been sent yet
        new_notification = {
            "notification_id": new_notification_id,
            "user_id": user_id,
            "home_id": None,
            "notification_type": notification_type,
            "title": title.strip(),
            "message": message.strip(),
            "muted": False,
            "related_device_id": None,
            "status": "pending",
            "sent_at": None,
            "read_at": None,
            "created_at": timestamp,
        }

        # Add notification to data (modify in place)
        notifications[new_notification_id] = new_notification

        return json.dumps({"success": True, "notification": new_notification})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """
        Tool schema for function-calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "compose_notification",
                "description": (
                    "Compose a notification configuration for a user. "
                    "Creates a notification record in pending status that can be used in automation routines. "
                    "The recipient can be specified by user_id or email. "
                    "The notification will not be sent until it is triggered by a routine or sent explicitly."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipient": {
                            "type": "string",
                            "description": "User ID or email address of the notification recipient (required).",
                        },
                        "title": {
                            "type": "string",
                            "description": "Title of the notification (required, max 255 characters).",
                        },
                        "message": {
                            "type": "string",
                            "description": "Message content of the notification (required, max 1000 characters).",
                        },
                        "notification_type": {
                            "type": "string",
                            "description": "Type of notification (optional, defaults to 'alert'). Valid values: 'alert', 'device_status', 'energy_summary'.",
                        },
                    },
                    "required": ["recipient", "title", "message"],
                },
            },
        }

