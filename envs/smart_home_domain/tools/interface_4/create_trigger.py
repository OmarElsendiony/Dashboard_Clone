import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateTrigger(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        automation_id: str,
        trigger_type: str,
        solar_event: Optional[str] = None,
        device_id: Optional[str] = None,
        schedule_id: Optional[str] = None,
        attribute_name: Optional[str] = None,
        attribute_value: Optional[str] = None,
        comparison_operator: Optional[str] = None,
    ) -> str:
        timestamp = "2025-12-19T23:59:00"

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        routines_dict = data.get("routines", {})
        if not isinstance(routines_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid routines container: expected dict at data['routines']",
                }
            )

        routine_triggers_dict = data.get("routine_triggers", {})
        if not isinstance(routine_triggers_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid routine_triggers container: expected dict at data['routine_triggers']",
                }
            )

        routine_trigger_attributes_dict = data.get("routine_trigger_attributes", {})
        if not isinstance(routine_trigger_attributes_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid routine_trigger_attributes container: expected dict at data['routine_trigger_attributes']",
                }
            )

        routine_schedule_dict = data.get("routine_schedules", {})
        if not isinstance(routine_schedule_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid routine_schedule container: expected dict at data['routine_schedule']",
                }
            )

        devices_dict = data.get("devices", {})
        if not isinstance(devices_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid devices container: expected dict at data['devices']",
                }
            )

        # Validate required parameters
        if not automation_id:
            return json.dumps({"success": False, "error": "automation_id is required"})

        if not trigger_type:
            return json.dumps({"success": False, "error": "trigger_type is required"})

        # Convert to strings for consistent comparison
        automation_id_str = str(automation_id).strip()
        trigger_type_str = str(trigger_type).strip()
        solar_event_str = str(solar_event).strip() if solar_event else None
        device_id_str = str(device_id).strip() if device_id else None
        schedule_id_str = str(schedule_id).strip() if schedule_id else None
        attribute_name_str = str(attribute_name).strip() if attribute_name else None
        attribute_value_str = str(attribute_value).strip() if attribute_value else None
        comparison_operator_str = (
            str(comparison_operator).strip() if comparison_operator else None
        )

        # Validate trigger_type
        valid_trigger_types = ["time_based", "solar_event", "device_state", "manual"]
        if trigger_type_str not in valid_trigger_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid trigger_type '{trigger_type_str}'. Must be one of: {', '.join(valid_trigger_types)}",
                }
            )

        # Check if automation exists
        if automation_id_str not in routines_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Automation with ID '{automation_id_str}' not found",
                }
            )

        automation = routines_dict[automation_id_str]
        if not isinstance(automation, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid automation data for ID '{automation_id_str}'",
                }
            )

        household_id_str = str(automation.get("home_id"))

        # Validate based on trigger_type
        if trigger_type_str == "time_based":
            if not schedule_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": "schedule_id is required for trigger_type 'time_based'",
                    }
                )

            # Validate schedule exists
            if schedule_id_str not in routine_schedule_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Schedule with ID '{schedule_id_str}' not found",
                    }
                )

            schedule = routine_schedule_dict[schedule_id_str]
            if not isinstance(schedule, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid schedule data for ID '{schedule_id_str}'",
                    }
                )

        elif trigger_type_str == "solar_event":
            if not solar_event_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": "solar_event is required for trigger_type 'solar_event'",
                    }
                )

            # Validate solar_event value
            valid_solar_events = ["sunrise", "sunset"]
            if solar_event_str not in valid_solar_events:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid solar_event '{solar_event_str}'. Must be one of: {', '.join(valid_solar_events)}",
                    }
                )

            if not schedule_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": "schedule_id is required for trigger_type 'solar_event'",
                    }
                )

            # Validate schedule exists
            if schedule_id_str not in routine_schedule_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Schedule with ID '{schedule_id_str}' not found",
                    }
                )

            schedule = routine_schedule_dict[schedule_id_str]
            if not isinstance(schedule, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid schedule data for ID '{schedule_id_str}'",
                    }
                )

        elif trigger_type_str == "device_state":
            if not device_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": "device_id is required for trigger_type 'device_state'",
                    }
                )

            if not attribute_name_str or not attribute_value_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": "attribute_name and attribute_value are required for trigger_type 'device_state'",
                    }
                )

            # Validate device exists
            if device_id_str not in devices_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Device with ID '{device_id_str}' not found",
                    }
                )

            device = devices_dict[device_id_str]
            if not isinstance(device, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid device data for ID '{device_id_str}'",
                    }
                )

            # Verify device belongs to the same household
            if str(device.get("home_id")) != household_id_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Device '{device_id_str}' does not belong to the same household as automation '{automation_id_str}'",
                    }
                )

            # Validate that device_type ends with 'sensor'
            device_type = str(device.get("device_type", ""))
            if not device_type.endswith("sensor"):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Device '{device_id_str}' has device_type '{device_type}' which is not a sensor. Only sensor devices can be used for device_state triggers.",
                    }
                )

            # Validate comparison_operator if provided
            if comparison_operator_str:
                valid_operators = [
                    "equals",
                    "greater_than",
                    "less_than",
                    "greater_equal",
                    "less_equal",
                ]
                if comparison_operator_str not in valid_operators:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid comparison_operator '{comparison_operator_str}'. Must be one of: {', '.join(valid_operators)}",
                        }
                    )

        # Generate new IDs
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        # Create routine_trigger entry
        new_trigger_id = generate_id(routine_triggers_dict)
        new_trigger = {
            "trigger_id": new_trigger_id,
            "routine_id": automation_id_str,
            "trigger_type": trigger_type_str,
            "routine_schedule_id": schedule_id_str,
            "solar_event": solar_event_str,
            "device_id": device_id_str,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        routine_triggers_dict[new_trigger_id] = new_trigger

        new_trigger_return = new_trigger.copy()
        new_trigger_return["automation_id"] = new_trigger_return.pop("routine_id")
        new_trigger_return["automation_schedule_id"] = new_trigger_return.pop("routine_schedule_id")

        # Create routine_trigger_attributes if device_state
        created_attributes = []
        if trigger_type_str == "device_state":
            new_attribute_id = generate_id(routine_trigger_attributes_dict)
            new_attribute = {
                "attribute_id": new_attribute_id,
                "trigger_id": new_trigger_id,
                "attribute_name": attribute_name_str,
                "attribute_value": attribute_value_str,
                "comparison_operator": comparison_operator_str,
                "created_at": timestamp,
            }
            routine_trigger_attributes_dict[new_attribute_id] = new_attribute
            created_attributes.append(new_attribute)

        result = {
            "success": True,
            "trigger": new_trigger_return,
            "message": f"Trigger successfully added to automation '{automation.get('routine_name')}' with ID: {new_trigger_id}",
        }

        if created_attributes:
            result["attributes"] = created_attributes

        return json.dumps(result)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_trigger",
                "description": (
                    "Create a trigger for an automation. "
                    "Validates that the automation exists. "
                    "trigger_type must be one of: time_based, solar_event, device_state, manual. "
                    "For 'time_based': schedule_id is required. Validates schedule exists. "
                    "For 'solar_event': solar_event (sunrise/sunset) and schedule_id are required. Validates schedule exists. "
                    "For 'device_state': device_id, attribute_name, and attribute_value are required. "
                    "Validates device exists, belongs to the same household, and device_type ends with 'sensor'. "
                    "Creates automation_trigger_attributes entry for device_state triggers. "
                    "Optional comparison_operator for device_state (equals, greater_than, less_than, greater_equal, less_equal). "
                    "For 'manual': no additional parameters required. "
                    "Attribute name and values are validated based on device type: camera (power: on/off, recording: recording/paused/stopped, motion_detection: motion_detected/clear), bulb (power: on/off, brightness: 0-100), thermostat (power: on/off, mode: heating/cooling/idle, temperature: 32-104, target_temperature: 60-90), speaker (power: on/off, playback_state: playing/paused/stopped, volume: 0-100, mute: muted/unmuted), door_lock (lock_state: locked/unlocked), motion_sensor (motion_state: motion_detected/clear), temperature_sensor (temperature: 32-104), humidity_sensor (humidity: 0-100), light_sensor (brightness_level: 0-65535), door_sensor (door_state: open/closed), water_leak_sensor (leak_state: leak_detected/no_leak), smoke_detector_sensor (smoke_state: smoke_detected/no_smoke/alarm_triggered), power_outlet (power: on/off, power_consumption: 0-3680), air_conditioner (power: on/off, mode: cooling/idle, temperature: 32-104, target_temperature: 60-85)."
                    "Returns the created trigger details and attributes (if applicable)."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "automation_id": {
                            "type": "string",
                            "description": "The ID of the automation to add the trigger to.",
                        },
                        "trigger_type": {
                            "type": "string",
                            "description": "The type of trigger. Accepted values: 'time_based', 'solar_event', 'device_state', 'manual'.",
                        },
                        "solar_event": {
                            "type": "string",
                            "description": "Required for trigger_type 'solar_event'. The solar event. Accepted values: 'sunrise', 'sunset'.",
                        },
                        "device_id": {
                            "type": "string",
                            "description": "Required for trigger_type 'device_state'. The ID of the sensor device that triggers the automation.",
                        },
                        "schedule_id": {
                            "type": "string",
                            "description": "Required for trigger_type 'time_based' and 'solar_event'. The ID of the schedule that defines when the trigger is active.",
                        },
                        "attribute_name": {
                            "type": "string",
                            "description": "Required for trigger_type 'device_state'. The name of the device attribute to monitor (e.g., 'motion_state', 'door_state', 'temperature').",
                        },
                        "attribute_value": {
                            "type": "string",
                            "description": "Required for trigger_type 'device_state'. The value of the attribute that triggers the automation (e.g., 'motion_detected', 'open', '75').",
                        },
                        "comparison_operator": {
                            "type": "string",
                            "description": "Optional for trigger_type 'device_state'. How to compare the attribute value. Accepted values: 'equals', 'greater_than', 'less_than', 'greater_equal', 'less_equal'.",
                        },
                    },
                    "required": ["automation_id", "trigger_type"],
                },
            },
        }
