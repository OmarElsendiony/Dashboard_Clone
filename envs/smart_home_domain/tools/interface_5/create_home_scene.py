import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateHomeScene(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        created_by_user_email: str,
        scene_name: str,
        description: Optional[str] = None,
        voice_control_phrase: Optional[str] = None,
    ) -> str:
        """
        Create a new scene.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        users = data.get("users")
        scenes = data.get("scenes")
        home_users = data.get("home_users")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(users, dict):
            return json.dumps({"success": False, "error": "users store missing"})
        if not isinstance(scenes, dict):
            return json.dumps({"success": False, "error": "scenes store missing"})
        if not isinstance(home_users, dict):
            return json.dumps({"success": False, "error": "home_users store missing"})

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

        if not isinstance(created_by_user_email, str) or not created_by_user_email.strip():
            return json.dumps({"success": False, "error": "created_by_user_email must be provided"})
        created_by_user_email = created_by_user_email.strip().lower()

        # Find user by email
        created_by_user_id = None
        for uid, u in users.items():
            if u.get("email", "").strip().lower() == created_by_user_email:
                created_by_user_id = uid
                break
        if not created_by_user_id:
            return json.dumps({"success": False, "error": f"User with email '{created_by_user_email}' not found"})
        
        # Verify user is admin of the home
        is_admin = False
        for hu_id, hu in home_users.items():
            if hu.get("home_id") == home_id and hu.get("user_id") == created_by_user_id and hu.get("role") == "admin":
                is_admin = True
                break
        if not is_admin:
            return json.dumps({"success": False, "error": f"User '{created_by_user_email}' must be an admin of home '{home_name}' to create scenes"})

        if not isinstance(scene_name, str) or not scene_name.strip():
            return json.dumps({"success": False, "error": "scene_name must be provided"})
        scene_name = scene_name.strip()

        for scene in scenes.values():
            if scene.get("home_id") == home_id and scene.get("scene_name", "").strip().lower() == scene_name.lower():
                return json.dumps({"success": False, "error": f"Scene '{scene_name}' already exists in this home"})

        desc = description.strip() if isinstance(description, str) and description.strip() else None
        voice_phrase = voice_control_phrase.strip() if isinstance(voice_control_phrase, str) and voice_control_phrase.strip() else None

        # Always create scenes in disabled status
        status_val = "disabled"

        scene_id = generate_id(scenes)
        timestamp = "2025-12-19T23:59:00"

        record = {
            "scene_id": scene_id,
            "home_id": home_id,
            "created_by_user_id": created_by_user_id,
            "scene_name": scene_name,
            "description": desc,
            "status": status_val,
            "voice_control_phrase": voice_phrase,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        scenes[scene_id] = record

        return json.dumps({
            "success": True,
            "scene": {
                "home_name": home_name,
                "scene_id": record.get("scene_id"),
                "scene_name": record.get("scene_name"),
                "description": record.get("description"),
                "status": record.get("status"),
                "voice_control_phrase": record.get("voice_control_phrase"),
                "created_by_user_email": created_by_user_email,
                "created_at": record.get("created_at"),
                "updated_at": record.get("updated_at"),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_home_scene",
                "description": "Create a new scene for a home. Scenes allow grouping multiple accessory actions that can be triggered together. The scene is created in disabled status by default and must be enabled before use. Only admin users can create scenes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "created_by_user_email": {
                            "type": "string",
                            "description": "Email address of the user creating the scene. Must be an admin of the home.",
                        },
                        "scene_name": {
                            "type": "string",
                            "description": "Name of the scene; must be unique within the home.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description of the scene.",
                        },
                        "voice_control_phrase": {
                            "type": "string",
                            "description": "Optional voice control activation phrase.",
                        },
                    },
                    "required": ["home_name", "created_by_user_email", "scene_name"],
                },
            },
        }

