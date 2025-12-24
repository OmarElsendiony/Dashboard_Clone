import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class MarkAsFavorite(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: str,
        home_id: str,
        entity_type: str,
        entity_id: str,
        favorite_name: str,
    ) -> str:
        """Mark a scene or device as a favorite for a user/home combination."""
        try:
            if not isinstance(data, dict):
                return json.dumps(
                    {"success": False, "error": "Invalid payload: data must be dict."}
                )

            users = data.get("users")
            scenes = data.get("scenes")
            devices = data.get("devices")
            favorite_devices = data.get("user_home_favorite_devices")
            favorite_scenes = data.get("user_home_favorite_scenes")

            if (
                not isinstance(users, dict)
                or not isinstance(scenes, dict)
                or not isinstance(devices, dict)
                or not isinstance(favorite_devices, dict)
                or not isinstance(favorite_scenes, dict)
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Missing user/device/scene/favorite collections in dataset.",
                    }
                )

            if not isinstance(user_id, str) or not user_id.strip():
                return json.dumps(
                    {"success": False, "error": "user_id is required for the favorite entry."}
                )

            user_id_clean = user_id.strip()
            if user_id_clean not in users:
                return json.dumps({"success": False, "error": "User not found."})

            if not isinstance(home_id, str) or not home_id.strip():
                return json.dumps(
                    {"success": False, "error": "home_id is required for the favorite entry."}
                )
            home_id_clean = home_id.strip()

            if not isinstance(entity_type, str) or not entity_type.strip():
                return json.dumps(
                    {"success": False, "error": "entity_type is required (device or scene)."}
                )
            entity_type_clean = entity_type.strip().lower()
            if entity_type_clean not in {"device", "scene"}:
                return json.dumps(
                    {"success": False, "error": "entity_type must be 'device' or 'scene'."}
                )

            if not isinstance(entity_id, str) or not entity_id.strip():
                return json.dumps(
                    {"success": False, "error": "entity_id is required to identify the device or scene."}
                )
            entity_id_clean = entity_id.strip()

            if not isinstance(favorite_name, str) or not favorite_name.strip():
                return json.dumps(
                    {"success": False, "error": "favorite_name must be a non-empty string."}
                )
            favorite_name_clean = favorite_name.strip()

            timestamp = "2025-12-19T23:59:00"

            def _generate_numeric_id(container: Dict[str, Any]) -> str:
                numeric_ids = []
                for key in container.keys():
                    try:
                        numeric_ids.append(int(str(key)))
                    except ValueError:
                        continue
                next_id = max(numeric_ids) + 1 if numeric_ids else len(container) + 1
                return str(next_id)

            if entity_type_clean == "device":
                device = devices.get(entity_id_clean)
                if not isinstance(device, dict):
                    return json.dumps({"success": False, "error": "Device not found."})
                if str(device.get("home_id", "")).strip() != home_id_clean:
                    return json.dumps(
                        {"success": False, "error": "Device belongs to a different household."}
                    )
                preference_id = _generate_numeric_id(favorite_devices)
                favorite_record = {
                    "preference_id": preference_id,
                    "user_id": user_id_clean,
                    "home_id": home_id_clean,
                    "favorite_name": favorite_name_clean,
                    "device_id": entity_id_clean,
                    "created_at": timestamp,
                    "updated_at": timestamp,
                }
                favorite_devices[preference_id] = favorite_record
                entity_payload = {"device_id": entity_id_clean}
            else:
                scene = scenes.get(entity_id_clean)
                if not isinstance(scene, dict):
                    return json.dumps({"success": False, "error": "Scene not found."})
                if str(scene.get("home_id", "")).strip() != home_id_clean:
                    return json.dumps(
                        {"success": False, "error": "Scene belongs to a different household."}
                    )
                preference_id = _generate_numeric_id(favorite_scenes)
                favorite_record = {
                    "preference_id": preference_id,
                    "user_id": user_id_clean,
                    "home_id": home_id_clean,
                    "favorite_name": favorite_name_clean,
                    "scene_id": entity_id_clean,
                    "created_at": timestamp,
                    "updated_at": timestamp,
                }
                favorite_scenes[preference_id] = favorite_record
                entity_payload = {"scene_id": entity_id_clean}

            return json.dumps(
                {
                    "success": True,
                    "message": f"{entity_type_clean.capitalize()} marked as favorite.",
                    "favorite": {
                        "preference_id": preference_id,
                        "user_id": user_id_clean,
                        "home_id": home_id_clean,
                        "favorite_name": favorite_name_clean,
                        **entity_payload,
                        "created_at": timestamp,
                        "updated_at": timestamp,
                    },
                }
            )
        except Exception as exc:
            return json.dumps(
                {"success": False, "error": f"Failed to mark as favorite: {exc}"}
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "mark_as_favorite",
                "description": (
                    "Mark a device or scene as a user favorite. Requires user_id, home_id, entity_type (device/scene), "
                    "entity_id, and a favorite_name label."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User identifier marking the favorite.",
                        },
                        "home_id": {
                            "type": "string",
                            "description": "Home identifier to scope the favorite.",
                        },
                        "entity_type": {
                            "type": "string",
                            "description": "Either 'device' or 'scene'.",
                        },
                        "entity_id": {
                            "type": "string",
                            "description": "ID of the device or scene being favorited.",
                        },
                        "favorite_name": {
                            "type": "string",
                            "description": "Label for the favorite entry.",
                        },
                    },
                    "required": ["user_id", "home_id", "entity_type", "entity_id", "favorite_name"],
                },
            },
        }
