import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class CreateSceneActivationAction(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        automation_id: str,
        scene_id: str,
    ) -> str:
        """
        Add a scene activation action to an automation.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        routines = data.get("routines")
        scenes = data.get("scenes")
        routine_actions = data.get("routine_actions")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(routines, dict):
            return json.dumps({"success": False, "error": "routines store missing"})
        if not isinstance(scenes, dict):
            return json.dumps({"success": False, "error": "scenes store missing"})
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

        if not isinstance(automation_id, str) or not automation_id.strip():
            return json.dumps({"success": False, "error": "automation_id must be provided"})
        automation_id = automation_id.strip()

        if automation_id not in routines:
            return json.dumps({"success": False, "error": f"Automation '{automation_id}' not found"})
        if routines[automation_id].get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Automation '{automation_id}' does not belong to home '{home_name}'"})

        if not isinstance(scene_id, str) or not scene_id.strip():
            return json.dumps({"success": False, "error": "scene_id must be provided"})
        scene_id = scene_id.strip()

        if scene_id not in scenes:
            return json.dumps({"success": False, "error": f"Scene '{scene_id}' not found"})

        if scenes[scene_id].get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Scene '{scene_id}' does not belong to home '{home_name}'"})

        action_id = generate_id(routine_actions)
        timestamp = "2025-12-19T23:59:00"

        action_record = {
            "action_id": action_id,
            "routine_id": automation_id,
            "action_type": "scene_activation",
            "target_device_id": None,
            "target_scene_id": scene_id,
            "target_notification_id": None,
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
                "scene_id": action_record.get("target_scene_id"),
                "created_at": action_record.get("created_at"),
                "updated_at": action_record.get("updated_at"),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_scene_activation_action",
                "description": "Create a scene activation action for a automation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "automation_id": {
                            "type": "string",
                            "description": "Identifier of the automation.",
                        },
                        "scene_id": {
                            "type": "string",
                            "description": "Identifier of the scene to activate.",
                        },
                    },
                    "required": ["home_name", "automation_id", "scene_id"],
                },
            },
        }

