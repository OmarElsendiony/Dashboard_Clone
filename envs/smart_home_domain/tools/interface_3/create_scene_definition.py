import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class CreateSceneDefinition(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        created_by_user_email: str,
        scene_name: str,
        status: str = "enabled",
        description: str = "",
    ) -> str:

        """Create a new scene for a household."""
        try:
            if not isinstance(data, dict):
                return json.dumps(
                    {"success": False, "error": "Invalid payload: data must be dict."}
                )

            homes = data.get("homes")
            users = data.get("users")
            scenes = data.get("scenes")

            if not isinstance(homes, dict) or not isinstance(users, dict) or not isinstance(scenes, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Missing homes, users, or scenes collections in dataset.",
                    }
                )

            if not isinstance(home_name, str) or not home_name.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "home_name is required so the household can be identified.",
                    }
                )

            if not isinstance(created_by_user_email, str) or not created_by_user_email.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "created_by_user_email is required to capture the acting user.",
                    }
                )

            if not isinstance(scene_name, str) or not scene_name.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "scene_name is required. Provide the descriptive scene label.",
                    }
                )

            home_name_clean = home_name.strip().lower()
            scene_name_clean = scene_name.strip()
            creator_email_clean = created_by_user_email.strip().lower()

            status_clean = status.strip().lower() if isinstance(status, str) else ""
            if status_clean not in {"enabled", "disabled"}:
                return json.dumps(
                    {
                        "success": False,
                        "error": "status must be 'enabled' or 'disabled'.",
                    }
                )

            matched_home = None
            for record in homes.values():
                if (
                    isinstance(record, dict)
                    and str(record.get("home_name", "")).strip().lower() == home_name_clean
                ):
                    matched_home = record
                    break

            if matched_home is None:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Household not found for the provided home_name.",
                    }
                )

            home_id = str(matched_home.get("home_id", "")).strip()
            if not home_id:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Matched household record is missing home_id.",
                    }
                )

            matched_user = None
            for record in users.values():
                if (
                    isinstance(record, dict)
                    and str(record.get("email", "")).strip().lower() == creator_email_clean
                ):
                    matched_user = record
                    break

            if matched_user is None:
                return json.dumps(
                    {
                        "success": False,
                        "error": "User not found for the provided email.",
                    }
                )

            if str(matched_user.get("status", "")).strip().lower() != "active":
                return json.dumps(
                    {
                        "success": False,
                        "error": "User must be active to create a scene.",
                    }
                )

            creator_user_id = str(matched_user.get("user_id", "")).strip()
            if not creator_user_id:
                return json.dumps(
                    {
                        "success": False,
                        "error": "User record is missing user_id.",
                    }
                )

            for record in scenes.values():
                if not isinstance(record, dict):
                    continue
                if (
                    str(record.get("home_id", "")).strip() == home_id
                    and str(record.get("scene_name", "")).strip().lower()
                    == scene_name_clean.lower()
                ):
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"A scene named '{scene_name_clean}' already exists in this household.",
                        }
                    )

            numeric_ids = []
            for key in scenes.keys():
                try:
                    numeric_ids.append(int(str(key)))
                except ValueError:
                    continue
            next_id = max(numeric_ids) + 1 if numeric_ids else len(scenes) + 1
            new_scene_id = str(next_id)
            timestamp = "2025-12-19T23:59:00"

            new_scene = {
                "scene_id": new_scene_id,
                "home_id": home_id,
                "created_by_user_id": creator_user_id,
                "scene_name": scene_name_clean,
                "description": description.strip() if isinstance(description, str) else "",
                "status": status_clean,
                "created_at": timestamp,
                "updated_at": timestamp,
            }
            scenes[new_scene_id] = new_scene

            return json.dumps(
                {
                    "success": True,
                    "message": f"Scene '{scene_name_clean}' created for household '{matched_home.get('home_name')}'.",
                    "scene": {
                        "scene_id": new_scene["scene_id"],
                        "scene_name": new_scene["scene_name"],
                        "status": new_scene["status"],
                        "home_id": new_scene["home_id"],
                        "home_name": matched_home.get("home_name"),
                        "created_by_user_id": new_scene["created_by_user_id"],
                        "created_by_user_email": matched_user.get("email"),
                        "description": new_scene["description"],
                        "created_at": new_scene["created_at"],
                        "updated_at": new_scene["updated_at"],
                    },
                }
            )
        except Exception as exc:
            return json.dumps(
                {"success": False, "error": f"Failed to create scene: {exc}"}
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_scene_definition",
                "description": (
                    "Create a new scene"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Required household name to identify which home the scene belongs to.",
                        },
                        "created_by_user_email": {
                            "type": "string",
                            "description": "Required email of the user creating the scene. User must exist and be active.",
                        },
                        "scene_name": {
                            "type": "string",
                            "description": "Required descriptive name for the scene. Must be unique within the household.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional initial status ('enabled' or 'disabled'). Defaults to 'enabled'.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional details about what the scene does. Defaults to empty string.",
                        },
                    },
                    "required": ["home_name", "created_by_user_email", "scene_name"],
                },
            },
        }
