import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class AddNotificationToScene(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        scene_id: str,
        notification_id: str,
    ) -> str:
        """
        Link a notification to a scene.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        scenes = data.get("scenes")
        notifications = data.get("notifications")
        scene_actions = data.get("scene_actions")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(scenes, dict):
            return json.dumps({"success": False, "error": "scenes store missing"})
        if not isinstance(notifications, dict):
            return json.dumps({"success": False, "error": "notifications store missing"})
        if not isinstance(scene_actions, dict):
            return json.dumps({"success": False, "error": "scene_actions store missing"})

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

        if not isinstance(scene_id, str) or not scene_id.strip():
            return json.dumps({"success": False, "error": "scene_id must be provided"})
        scene_id = scene_id.strip()

        if scene_id not in scenes:
            return json.dumps({"success": False, "error": f"Scene '{scene_id}' not found"})

        if scenes[scene_id].get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Scene '{scene_id}' does not belong to home '{home_name}'"})

        if not isinstance(notification_id, str) or not notification_id.strip():
            return json.dumps({"success": False, "error": "notification_id must be provided"})
        notification_id = notification_id.strip()

        if notification_id not in notifications:
            return json.dumps({"success": False, "error": f"Notification '{notification_id}' not found"})

        notification = notifications[notification_id]
        if notification.get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Notification '{notification_id}' does not belong to home '{home_name}'"})

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        timestamp = "2025-12-19T23:59:00"
        scene_action_id = generate_id(scene_actions)
        scene_actions[scene_action_id] = {
            "scene_action_id": scene_action_id,
            "scene_id": scene_id,
            "device_id": None,
            "action_type": "notification",
            "target_notification_id": notification_id,
            "created_at": timestamp,
        }

        return json.dumps({
            "success": True,
            "message": "Notification linked to scene",
            "scene_id": scene_id,
            "notification_id": notification_id,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_notification_to_scene",
                "description": "Add a notification trigger to a scene.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "scene_id": {
                            "type": "string",
                            "description": "Identifier of the scene.",
                        },
                        "notification_id": {
                            "type": "string",
                            "description": "Identifier of the notification.",
                        },
                    },
                    "required": ["home_name", "scene_id", "notification_id"],
                },
            },
        }

