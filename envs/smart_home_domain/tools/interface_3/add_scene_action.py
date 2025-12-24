import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class AddSceneAction(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        scene_id: str,
        device_id: str,
    ) -> str:
        """Attach a device action to scene."""
        try:
            if not isinstance(data, dict):
                return json.dumps(
                    {"success": False, "error": "Invalid payload: data must be dict."}
                )

            scenes = data.get("scenes")
            devices = data.get("devices")
            scene_actions = data.get("scene_actions")

            if (
                not isinstance(scenes, dict)
                or not isinstance(devices, dict)
                or not isinstance(scene_actions, dict)
            ):
                return json.dumps(
                    {"success": False, "error": "Missing scene/device/action collections in dataset."}
                )

            if not isinstance(scene_id, str) or not scene_id.strip():
                return json.dumps(
                    {"success": False, "error": "scene_id is required to identify the scene."}
                )

            scene_id_clean = scene_id.strip()
            scene = scenes.get(scene_id_clean)
            if not isinstance(scene, dict):
                return json.dumps(
                    {"success": False, "error": "Scene not found in dataset."}
                )

            if not isinstance(device_id, str) or not device_id.strip():
                return json.dumps(
                    {"success": False, "error": "device_id is required to attach to the scene."}
                )

            device_id_clean = device_id.strip()
            device = devices.get(device_id_clean)
            if not isinstance(device, dict):
                return json.dumps(
                    {"success": False, "error": "Device not found in dataset."}
                )

            if str(device.get("home_id", "")).strip() != str(scene.get("home_id", "")).strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "Device belongs to a different household; select a device from the same home.",
                    }
                )
            def _generate_numeric_id(container: Dict[str, Any]) -> str:
                numeric_ids = []
                for key in container.keys():
                    try:
                        numeric_ids.append(int(str(key)))
                    except ValueError:
                        continue
                next_id = max(numeric_ids) + 1 if numeric_ids else len(container) + 1
                return str(next_id)
            scene_action_id = _generate_numeric_id(scene_actions)
            timestamp = "2025-12-19T23:59:00"

            new_action = {
                "scene_action_id": scene_action_id,
                "scene_id": scene_id_clean,
                "device_id": device_id_clean,
                "created_at": timestamp,
            }
            scene_actions[scene_action_id] = new_action

            return json.dumps(
                {
                    "success": True,
                    "message": "Device action added to scene.",
                    "scene_action": {
                        "scene_action_id": scene_action_id,
                        "scene_id": scene_id_clean,
                        "device_id": device_id_clean,
                        "created_at": timestamp,
                    },
                }
            )
        except Exception as exc:
            return json.dumps(
                {"success": False, "error": f"Failed to add scene action: {exc}"}
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_scene_action",
                "description": (
                    "Add a device action to a scene. Requires scene_id and device_id (must belong to the same household)."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scene_id": {
                            "type": "string",
                            "description": "Required identifier of the scene receiving the action.",
                        },
                        "device_id": {
                            "type": "string",
                            "description": "Required identifier of the device to control.",
                        },
                    },
                    "required": ["scene_id", "device_id"],
                },
            },
        }
