import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class DuplicateHomeScene(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        source_scene_id: str,
        new_scene_name: str,
    ) -> str:
        """
        Create a copy of a scene with all its actions.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

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
        if not isinstance(scene_actions, dict):
            return json.dumps({"success": False, "error": "scene_actions store missing"})
        if not isinstance(scene_action_attributes, dict):
            return json.dumps({"success": False, "error": "scene_action_attributes store missing"})

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

        if not isinstance(source_scene_id, str) or not source_scene_id.strip():
            return json.dumps({"success": False, "error": "source_scene_id must be provided"})
        source_scene_id = source_scene_id.strip()

        if source_scene_id not in scenes:
            return json.dumps({"success": False, "error": f"Scene '{source_scene_id}' not found"})

        original_scene = scenes[source_scene_id]
        if original_scene.get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Scene '{source_scene_id}' does not belong to home '{home_name}'"})

        if not isinstance(new_scene_name, str) or not new_scene_name.strip():
            return json.dumps({"success": False, "error": "new_scene_name must be provided"})
        new_scene_name = new_scene_name.strip()

        for scene in scenes.values():
            if scene.get("home_id") == original_scene.get("home_id") and scene.get("scene_name", "").strip().lower() == new_scene_name.lower():
                return json.dumps({"success": False, "error": f"Scene '{new_scene_name}' already exists in this home"})

        new_scene_id = generate_id(scenes)
        timestamp = "2025-12-19T23:59:00"

        new_scene = {
            "scene_id": new_scene_id,
            "home_id": original_scene.get("home_id"),
            "created_by_user_id": original_scene.get("created_by_user_id"),
            "scene_name": new_scene_name,
            "description": original_scene.get("description"),
            "status": original_scene.get("status"),
            "voice_control_phrase": original_scene.get("voice_control_phrase"),
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        scenes[new_scene_id] = new_scene

        action_mapping = {}
        new_actions_to_add = {}
        for action_id, action in scene_actions.items():
            if action.get("scene_id") == source_scene_id:
                new_action_id = generate_id({**scene_actions, **new_actions_to_add})
                new_action = {
                    "scene_action_id": new_action_id,
                    "scene_id": new_scene_id,
                    "device_id": action.get("device_id"),
                    "created_at": timestamp,
                }
                new_actions_to_add[new_action_id] = new_action
                action_mapping[action_id] = new_action_id
        
        # Add new actions after iteration
        scene_actions.update(new_actions_to_add)

        new_attrs_to_add = {}
        for attr_id, attr in scene_action_attributes.items():
            original_action_id = attr.get("scene_action_id")
            if original_action_id in action_mapping:
                new_attr_id = generate_id({**scene_action_attributes, **new_attrs_to_add})
                new_attr = {
                    "attribute_id": new_attr_id,
                    "scene_action_id": action_mapping[original_action_id],
                    "attribute_name": attr.get("attribute_name"),
                    "attribute_value": attr.get("attribute_value"),
                    "created_at": timestamp,
                }
                new_attrs_to_add[new_attr_id] = new_attr
        
        # Add new attributes after iteration
        scene_action_attributes.update(new_attrs_to_add)

        # Prepare scene actions with their attributes for output
        actions_output = []
        for new_action_id, new_action in new_actions_to_add.items():
            action_attrs = []
            for attr_id, attr in new_attrs_to_add.items():
                if attr.get("scene_action_id") == new_action_id:
                    action_attrs.append({
                        "attribute_name": attr.get("attribute_name"),
                        "attribute_value": attr.get("attribute_value"),
                        "created_at": attr.get("created_at"),
                    })
            
            actions_output.append({
                "scene_action_id": new_action.get("scene_action_id"),
                "device_id": new_action.get("device_id"),
                "attributes": action_attrs,
                "created_at": new_action.get("created_at"),
            })

        return json.dumps({
            "success": True,
            "scene": {
                "home_name": home_name,
                "scene_id": new_scene.get("scene_id"),
                "scene_name": new_scene.get("scene_name"),
                "description": new_scene.get("description"),
                "status": new_scene.get("status"),
                "voice_control_phrase": new_scene.get("voice_control_phrase"),
                "created_at": new_scene.get("created_at"),
                "updated_at": new_scene.get("updated_at"),
            },
            "scene_actions": actions_output,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "duplicate_home_scene",
                "description": "Duplicate an existing scene with all its actions and settings. This creates a complete copy of the source scene including all accessory control actions, their attributes, and scene configuration. The duplicated scene will have the same description, status, and voice control phrase as the original, but with a new unique name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home where the scene exists and will be duplicated. The source scene must belong to this home.",
                        },
                        "source_scene_id": {
                            "type": "string",
                            "description": "Identifier of the existing scene to duplicate. This scene must exist in the specified home. All actions, accessory controls, and attributes associated with this scene will be copied to the new scene.",
                        },
                        "new_scene_name": {
                            "type": "string",
                            "description": "Name for the new duplicated scene; must be unique within the home. This will be the display name for the copied scene. The new scene will inherit all other properties from the source scene.",
                        },
                    },
                    "required": ["home_name", "source_scene_id", "new_scene_name"],
                },
            },
        }

