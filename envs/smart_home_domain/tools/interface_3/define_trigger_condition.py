import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class DefineTriggerCondition(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        trigger_id: str,
        attribute_name: str,
        comparison_operator: str,
        attribute_value: str,
    ) -> str:
        """Add a comparison condition to an existing flow trigger."""
        try:
            if not isinstance(data, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Invalid payload: data must be the state dictionary.",
                    }
                )

            triggers = data.get("routine_triggers")
            trigger_attributes = data.get("routine_trigger_attributes")

            if not isinstance(triggers, dict) or not isinstance(trigger_attributes, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Missing trigger or trigger_attributes collections in the  dataset.",
                    }
                )

            if not isinstance(trigger_id, str) or not trigger_id.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "trigger_id is required so the trigger can be identified.",
                    }
                )

            trigger_id_clean = trigger_id.strip()
            trigger_record = triggers.get(trigger_id_clean)
            if not isinstance(trigger_record, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Trigger not found.",
                    }
                )

            if str(trigger_record.get("trigger_type", "")).strip().lower() != "device_state":
                return json.dumps(
                    {
                        "success": False,
                        "error": "define_trigger_condition only applies to device_state triggers.",
                    }
                )

            if not isinstance(attribute_name, str) or not attribute_name.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "attribute_name is required. Provide the sensor field or state name.",
                    }
                )

            if not isinstance(comparison_operator, str) or not comparison_operator.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "comparison_operator is required. Use equals, greater_than, greater_equal, less_than, or less_equal.",
                    }
                )

            operator_clean = comparison_operator.strip().lower()
            allowed_ops = {"equals", "greater_than", "greater_equal", "less_than", "less_equal"}
            if operator_clean not in allowed_ops:
                return json.dumps(
                    {
                        "success": False,
                        "error": "comparison_operator must be one of equals, greater_than, greater_equal, less_than, or less_equal.",
                    }
                )

            if not isinstance(attribute_value, str) or not attribute_value.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "attribute_value is required. Provide the state or numeric value to compare against.",
                    }
                )

            numeric_ids = []
            for key in trigger_attributes.keys():
                try:
                    numeric_ids.append(int(str(key)))
                except ValueError:
                    continue
            next_id = max(numeric_ids) + 1 if numeric_ids else len(trigger_attributes) + 1
            attribute_id = str(next_id)

            timestamp = "2025-12-19T23:59:00"
            new_attribute = {
                "attribute_id": attribute_id,
                "trigger_id": trigger_id_clean,
                "attribute_name": attribute_name.strip(),
                "attribute_value": attribute_value.strip(),
                "comparison_operator": operator_clean,
                "created_at": timestamp,
            }
            trigger_attributes[attribute_id] = new_attribute

            return json.dumps(
                {
                    "success": True,
                    "message": "Trigger condition defined successfully.",
                    "condition": {
                        "attribute_id": new_attribute["attribute_id"],
                        "trigger_id": new_attribute["trigger_id"],
                        "attribute_name": new_attribute["attribute_name"],
                        "attribute_value": new_attribute["attribute_value"],
                        "comparison_operator": new_attribute["comparison_operator"],
                        "created_at": new_attribute["created_at"],
                    },
                }
            )
        except Exception as exc:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Failed to define trigger condition: {exc}",
                }
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "define_trigger_condition",
                "description": (
                    "Attach attribute-level conditions to a flow trigger. "
                    "Requires trigger_id, attribute_name, comparison_operator (equals/greater_than/greater_equal/less_than/less_equal), and attribute_value."
                    "Device attributes are validated based on device type: camera (power: on/off, recording: recording/paused/stopped, motion_detection: motion_detected/clear), bulb (power: on/off, brightness: 0-100), thermostat (power: on/off, mode: heating/cooling/idle, temperature: 32-104, target_temperature: 60-90), speaker (power: on/off, playback_state: playing/paused/stopped, volume: 0-100, mute: muted/unmuted), door_lock (lock_state: locked/unlocked), motion_sensor (motion_state: motion_detected/clear), temperature_sensor (temperature: 32-104), humidity_sensor (humidity: 0-100), light_sensor (brightness_level: 0-65535), door_sensor (door_state: open/closed), water_leak_sensor (leak_state: leak_detected/no_leak), smoke_detector_sensor (smoke_state: smoke_detected/no_smoke/alarm_triggered), power_outlet (power: on/off, power_consumption: 0-3680), air_conditioner (power: on/off, mode: cooling/idle, temperature: 32-104, target_temperature: 60-85)."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "trigger_id": {
                            "type": "string",
                            "description": "Required identifier of the trigger",
                        },
                        "attribute_name": {
                            "type": "string",
                            "description": "Required sensor field or state name",
                        },
                        "comparison_operator": {
                            "type": "string",
                            "description": "Required comparison operator: equals, greater_than, greater_equal, less_than, or less_equal.",
                        },
                        "attribute_value": {
                            "type": "string",
                            "description": "Required value to compare against",
                        },
                    },
                    "required": ["trigger_id", "attribute_name", "comparison_operator", "attribute_value"],
                },
            },
        }
