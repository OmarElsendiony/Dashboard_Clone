import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateNotificationAction(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        notification_id: str,
        automation_id: Optional[str] = None,
        automation_name: Optional[str] = None,
    ) -> str:
        """
        Add a notification action to an automation.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        routines = data.get("routines")
        notifications = data.get("notifications")
        routine_actions = data.get("routine_actions")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(routines, dict):
            return json.dumps({"success": False, "error": "routines store missing"})
        if not isinstance(notifications, dict):
            return json.dumps({"success": False, "error": "notifications store missing"})
        if not isinstance(routine_actions, dict):
            return json.dumps({"success": False, "error": "routine_actions store missing"})

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

        # Exactly one of automation_id or automation_name must be provided
        if (automation_id is None and automation_name is None) or (automation_id is not None and automation_name is not None):
            return json.dumps({"success": False, "error": "Provide exactly one of automation_id or automation_name"})

        resolved_automation_id = None
        if automation_id is not None:
            if not isinstance(automation_id, str) or not automation_id.strip():
                return json.dumps({"success": False, "error": "automation_id must be a non-empty string"})
            resolved_automation_id = automation_id.strip()
            if resolved_automation_id not in routines:
                return json.dumps({"success": False, "error": f"Automation '{resolved_automation_id}' not found"})
        else:
            if not isinstance(automation_name, str) or not automation_name.strip():
                return json.dumps({"success": False, "error": "automation_name must be a non-empty string"})
            name_val = automation_name.strip().lower()
            matches = []
            for rid, r in routines.items():
                if r.get("home_id") == home_id and r.get("routine_name", "").strip().lower() == name_val:
                    matches.append(rid)
            if not matches:
                return json.dumps({"success": False, "error": f"Automation '{automation_name.strip()}' not found"})
            if len(matches) > 1:
                return json.dumps({"success": False, "error": f"Multiple automations named '{automation_name.strip()}' found in home '{home_name}'"})
            resolved_automation_id = matches[0]

        if routines[resolved_automation_id].get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Automation '{resolved_automation_id}' does not belong to home '{home_name}'"})

        if not isinstance(notification_id, str) or not notification_id.strip():
            return json.dumps({"success": False, "error": "notification_id must be provided"})
        notification_id = notification_id.strip()

        if notification_id not in notifications:
            return json.dumps({"success": False, "error": f"Notification '{notification_id}' not found"})

        if notifications[notification_id].get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Notification '{notification_id}' does not belong to home '{home_name}'"})

        action_id = generate_id(routine_actions)
        timestamp = "2025-12-19T23:59:00"

        action_record = {
            "action_id": action_id,
            "routine_id": resolved_automation_id,
            "action_type": "notification",
            "target_device_id": None,
            "target_scene_id": None,
            "target_notification_id": notification_id,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        routine_actions[action_id] = action_record

        return json.dumps({
            "success": True,
            "action": {
                "action_id": action_record.get("action_id"),
                "automation_id": action_record.get("routine_id"),
                "action_type": action_record.get("action_type"),
                "notification_id": action_record.get("target_notification_id"),
                "created_at": action_record.get("created_at"),
                "updated_at": action_record.get("updated_at"),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_notification_action",
                "description": "Create a notification action for an automation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "automation_id": {
                            "type": "string",
                            "description": "Optional identifier of the automation (provide either automation_id or automation_name).",
                        },
                        "automation_name": {
                            "type": "string",
                            "description": "Optional name of the automation (provide either automation_id or automation_name).",
                        },
                        "notification_id": {
                            "type": "string",
                            "description": "Identifier of the notification to send.",
                        },
                    },
                    "required": ["home_name", "notification_id"],
                },
            },
        }

