import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class DeleteHomeScene(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        scene_id: str,
    ) -> str:
        """
        Delete a scene and cascade delete related actions.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        scenes = data.get("scenes")
        scene_actions = data.get("scene_actions")
        scene_action_attributes = data.get("scene_action_attributes")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(scenes, dict):
            return json.dumps({"success": False, "error": "scenes store missing"})

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

        deleted_scene = scenes.pop(scene_id)

        if isinstance(scene_actions, dict):
            action_ids_to_delete = [k for k, v in scene_actions.items() if v.get("scene_id") == scene_id]
            
            if isinstance(scene_action_attributes, dict):
                for attr_id in list(scene_action_attributes.keys()):
                    if scene_action_attributes[attr_id].get("scene_action_id") in action_ids_to_delete:
                        scene_action_attributes.pop(attr_id)
            
            for action_id in action_ids_to_delete:
                scene_actions.pop(action_id)

        return json.dumps({
            "success": True,
            "deleted_scene": {
                "home_name": home_name,
                "scene_id": deleted_scene.get("scene_id") or scene_id,
                "scene_name": deleted_scene.get("scene_name"),
                "description": deleted_scene.get("description"),
                "status": deleted_scene.get("status"),
                "voice_control_phrase": deleted_scene.get("voice_control_phrase"),
                "created_at": deleted_scene.get("created_at"),
                "updated_at": deleted_scene.get("updated_at"),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "delete_home_scene",
                "description": "Delete a scene and all its actions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "scene_id": {
                            "type": "string",
                            "description": "Identifier of the scene to delete.",
                        },
                    },
                    "required": ["home_name", "scene_id"],
                },
            },
        }

