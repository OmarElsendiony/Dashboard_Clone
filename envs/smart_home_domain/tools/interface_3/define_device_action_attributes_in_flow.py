import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class DefineDeviceActionAttributesInFlow(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action_id: str,
        attributes: Dict[str, str],
    ) -> str:
        try:
            """Attach attribute key/value pairs to a device action within a flow."""
            if not isinstance(data, dict):
                return json.dumps(
                    {"success": False, "error": "Invalid payload: data must be dict."}
                )

            actions = data.get("routine_actions")
            action_attributes = data.get("routine_action_attributes")

            if not isinstance(actions, dict) or not isinstance(action_attributes, dict):
                return json.dumps(
                    {"success": False, "error": "Missing routine_actions or routine_action_attributes collections."}
                )

            if not isinstance(action_id, str) or not action_id.strip():
                return json.dumps({"success": False, "error": "action_id is required."})

            action_id_clean = action_id.strip()
            action_record = actions.get(action_id_clean)
            if not isinstance(action_record, dict):
                return json.dumps({"success": False, "error": "Flow action not found."})

            if not isinstance(attributes, dict) or not attributes:
                return json.dumps(
                    {"success": False, "error": "attributes must be a non-empty dictionary of key/value strings."}
                )

            cleaned_attributes = {}
            for key, value in attributes.items():
                if not isinstance(key, str) or not key.strip():
                    return json.dumps(
                        {"success": False, "error": "Attribute names must be non-empty strings."}
                    )
                if not isinstance(value, str) or not value.strip():
                    return json.dumps(
                        {"success": False, "error": "Attribute values must be non-empty strings."}
                    )
                cleaned_attributes[key.strip()] = value.strip()

            def _generate_numeric_id(container: Dict[str, Any]) -> str:
                numeric_ids = []
                for key in container.keys():
                    try:
                        numeric_ids.append(int(str(key)))
                    except ValueError:
                        continue
                next_id = max(numeric_ids) + 1 if numeric_ids else len(container) + 1
                return str(next_id)

            timestamp = "2025-12-19T23:59:00"
            created_payloads = []

            for key, value in cleaned_attributes.items():
                attribute_id = _generate_numeric_id(action_attributes)
                payload = {
                    "attribute_id": attribute_id,
                    "action_id": action_id_clean,
                    "attribute_name": key,
                    "attribute_value": value,
                    "created_at": timestamp,
                }
                action_attributes[attribute_id] = payload
                created_payloads.append(payload)

            return json.dumps(
                {
                    "success": True,
                    "message": "Device action attributes defined successfully.",
                    "action_id": action_id_clean,
                    "attributes": created_payloads,
                }
            )

        except Exception as exc:
            return json.dumps(
                {"success": False, "error": f"Failed to define device action attributes in flow: {exc}"}
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "define_device_action_attributes_in_flow",
                "description": (
                    "Attach attribute key/value pairs to a device control action within a flow."
                    "Device attributes are validated based on device type: camera (power: on/off, recording: recording/paused/stopped, motion_detection: motion_detected/clear), bulb (power: on/off, brightness: 0-100), thermostat (power: on/off, mode: heating/cooling/idle, temperature: 32-104, target_temperature: 60-90), speaker (power: on/off, playback_state: playing/paused/stopped, volume: 0-100, mute: muted/unmuted), door_lock (lock_state: locked/unlocked), motion_sensor (motion_state: motion_detected/clear), temperature_sensor (temperature: 32-104), humidity_sensor (humidity: 0-100), light_sensor (brightness_level: 0-65535), door_sensor (door_state: open/closed), water_leak_sensor (leak_state: leak_detected/no_leak), smoke_detector_sensor (smoke_state: smoke_detected/no_smoke/alarm_triggered), power_outlet (power: on/off, power_consumption: 0-3680), air_conditioner (power: on/off, mode: cooling/idle, temperature: 32-104, target_temperature: 60-85)."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action_id": {
                            "type": "string",
                            "description": "Required routine action identifier.",
                        },
                        "attributes": {
                            "type": "object",
                            "description": (
                                "Dictionary of attribute_name: attribute_value pairs. "
                                "Sample Value: "
                                "{"
                                "\"camera\": {\"power\": [\"on\", \"off\"], \"recording\": [\"recording\", \"paused\", \"stopped\"], \"motion_detection\": [\"motion_detected\", \"clear\"]}, "
                                "\"bulb\": {\"power\": [\"on\", \"off\"], \"brightness\": \"0 to 100 %\"}, "
                                "\"thermostat\": {\"power\": [\"on\", \"off\"], \"mode\": [\"heating\", \"cooling\", \"idle\"], \"temperature\": \"32 to 104 °F\", \"target_temperature\": \"60 to 90 °F\"}, "
                                "\"speaker\": {\"power\": [\"on\", \"off\"], \"playback_state\": [\"playing\", \"paused\", \"stopped\"], \"volume\": \"0 to 100 %\", \"mute\": [\"muted\", \"unmuted\"]}, "
                                "\"door_lock\": {\"lock_state\": [\"locked\", \"unlocked\"]}, "
                                "\"motion_sensor\": {\"motion_state\": [\"motion_detected\", \"clear\"]}, "
                                "\"temperature_sensor\": {\"temperature\": \"32 to 104 °F\"}, "
                                "\"humidity_sensor\": {\"humidity\": \"0 to 100 %\"}, "
                                "\"light_sensor\": {\"brightness_level\": \"0 to 65535 lux\"}, "
                                "\"door_sensor\": {\"door_state\": [\"open\", \"closed\"]}, "
                                "\"water_leak_sensor\": {\"leak_state\": [\"leak_detected\", \"no_leak\"]}, "
                                "\"smoke_detector_sensor\": {\"smoke_state\": [\"smoke_detected\", \"no_smoke\", \"alarm_triggered\"]}, "
                                "\"power_outlet\": {\"power\": [\"on\", \"off\"], \"power_consumption\": \"0 to 3680 watts\"}, "
                                "\"air_conditioner\": {\"power\": [\"on\", \"off\"], \"mode\": [\"cooling\", \"idle\"], \"temperature\": \"32 to 104 °F\", \"target_temperature\": \"60 to 85 °F\"}"
                                "}"
                            ),
                        },
                    },
                    "required": ["action_id", "attributes"],
                },
            },
        }
