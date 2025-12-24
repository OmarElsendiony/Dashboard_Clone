import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class SetSceneDeviceState(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        scene_id: str,
        device_id: str,
        scene_action_id: str,
        attribute_name: str,
        attribute_value: str,
    ) -> str:
        """Update or create a device-level attribute for a scene action."""
        try:
            if not isinstance(data, dict):
                return json.dumps(
                    {"success": False, "error": "Invalid payload: data must be dict."}
                )

            scenes = data.get("scenes")
            devices = data.get("devices")
            scene_actions = data.get("scene_actions")
            scene_action_attributes = data.get("scene_action_attributes")

            if (
                not isinstance(scenes, dict)
                or not isinstance(devices, dict)
                or not isinstance(scene_actions, dict)
                or not isinstance(scene_action_attributes, dict)
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Missing scenes/devices/actions collections in the dataset.",
                    }
                )

            if not isinstance(scene_id, str) or not scene_id.strip():
                return json.dumps(
                    {"success": False, "error": "scene_id is required to identify the scene."}
                )
            scene_id_clean = scene_id.strip()
            scene = scenes.get(scene_id_clean)
            if not isinstance(scene, dict):
                return json.dumps({"success": False, "error": "Scene not found."})

            if not isinstance(device_id, str) or not device_id.strip():
                return json.dumps(
                    {"success": False, "error": "device_id is required to identify the device."}
                )
            device_id_clean = device_id.strip()
            device = devices.get(device_id_clean)
            if not isinstance(device, dict):
                return json.dumps({"success": False, "error": "Device not found."})

            if str(device.get("home_id", "")).strip() != str(scene.get("home_id", "")).strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "Device belongs to a different household; select a device within the same home.",
                    }
                )

            if not isinstance(attribute_name, str) or not attribute_name.strip():
                return json.dumps(
                    {"success": False, "error": "attribute_name must be a non-empty string."}
                )
            attribute_name_clean = attribute_name.strip()

            if not isinstance(attribute_value, str) or not attribute_value.strip():
                return json.dumps(
                    {"success": False, "error": "attribute_value must be a non-empty string."}
                )
            attribute_value_clean = attribute_value.strip()

            if not isinstance(scene_action_id, str) or not scene_action_id.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "scene_action_id must be provided to target the correct action.",
                    }
                )
            scene_action_id_clean = scene_action_id.strip()
            matching_action = scene_actions.get(scene_action_id_clean)
            if not isinstance(matching_action, dict):
                return json.dumps(
                    {"success": False, "error": "Scene action not found for provided scene_action_id."}
                )
            if (
                str(matching_action.get("scene_id", "")).strip() != scene_id_clean
                or str(matching_action.get("device_id", "")).strip() != device_id_clean
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": "scene_action_id does not belong to the supplied scene_id and device_id.",
                    }
                )

            scene_action_id = scene_action_id_clean
            timestamp = "2025-12-19T23:59:00"

            existing_attribute = None
            existing_attribute_id = None
            for attr_id, attr_record in scene_action_attributes.items():
                if not isinstance(attr_record, dict):
                    continue
                if (
                    str(attr_record.get("scene_action_id", "")).strip() == scene_action_id
                    and str(attr_record.get("attribute_name", "")).strip().lower()
                    == attribute_name_clean.lower()
                ):
                    existing_attribute = attr_record
                    existing_attribute_id = attr_id
                    break

            def _generate_numeric_id(container: Dict[str, Any]) -> str:
                numeric_ids = []
                for key in container.keys():
                    try:
                        numeric_ids.append(int(str(key)))
                    except ValueError:
                        continue
                next_id = max(numeric_ids) + 1 if numeric_ids else len(container) + 1
                return str(next_id)

            if existing_attribute is None:
                attribute_id = _generate_numeric_id(scene_action_attributes)
                payload = {
                    "attribute_id": attribute_id,
                    "scene_action_id": scene_action_id,
                    "attribute_name": attribute_name_clean,
                    "attribute_value": attribute_value_clean,
                    "created_at": timestamp,
                }
                scene_action_attributes[attribute_id] = payload
                result_payload = payload
                operation = "created"
            else:
                existing_attribute["attribute_value"] = attribute_value_clean
                existing_attribute["created_at"] = timestamp
                result_payload = {
                    "attribute_id": existing_attribute_id,
                    "scene_action_id": scene_action_id,
                    "attribute_name": attribute_name_clean,
                    "attribute_value": attribute_value_clean,
                    "created_at": timestamp,
                }
                operation = "updated"

            return json.dumps(
                {
                    "success": True,
                    "message": f"Scene device state {operation} successfully.",
                    "scene_action": {
                        "scene_action_id": scene_action_id,
                        "scene_id": scene_id_clean,
                        "device_id": device_id_clean,
                    },
                    "attribute": result_payload,
                }
            )
        except Exception as exc:
            return json.dumps(
                {"success": False, "error": f"Failed to set scene device state: {exc}"}
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "set_scene_device_state",
                "description": (
                    "Set or update a state attribute for a device within a scene. "
                    "Requires scene_id, device_id (already linked via add_scene_action), and an attribute name/value pair."
                    "Device attributes are validated based on device type: camera (power: on/off, recording: recording/paused/stopped, motion_detection: motion_detected/clear), bulb (power: on/off, brightness: 0-100), thermostat (power: on/off, mode: heating/cooling/idle, temperature: 32-104, target_temperature: 60-90), speaker (power: on/off, playback_state: playing/paused/stopped, volume: 0-100, mute: muted/unmuted), door_lock (lock_state: locked/unlocked), motion_sensor (motion_state: motion_detected/clear), temperature_sensor (temperature: 32-104), humidity_sensor (humidity: 0-100), light_sensor (brightness_level: 0-65535), door_sensor (door_state: open/closed), water_leak_sensor (leak_state: leak_detected/no_leak), smoke_detector_sensor (smoke_state: smoke_detected/no_smoke/alarm_triggered), power_outlet (power: on/off, power_consumption: 0-3680), air_conditioner (power: on/off, mode: cooling/idle, temperature: 32-104, target_temperature: 60-85)."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scene_id": {
                            "type": "string",
                            "description": "Scene identifier that already contains the device action.",
                        },
                        "device_id": {
                            "type": "string",
                            "description": "Device identifier already linked to the scene.",
                        },
                        "scene_action_id": {
                            "type": "string",
                            "description": "Specific action identifier representing the device’s entry inside the scene.",
                        },
                        "attribute_name": {
                            "type": "string",
                            "description": "State field to set (e.g., power, brightness).",
                        },
                        "attribute_value": {
                            "type": "string",
                            "description": "State value to store for the device when the scene runs.",
                        },
                    },
                    "required": ["scene_id", "device_id", "scene_action_id", "attribute_name", "attribute_value"],
                },
            },
        }
