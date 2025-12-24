import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class TriggerRoutine(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        routine_id: str,
        trigger_type: str,
        routine_schedule_id: Optional[str] = None,
        solar_event: Optional[str] = None,
        device_id: Optional[str] = None,
        trigger_attributes: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a trigger for a routine.
        """
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        def get_device_attribute_constraints():
            """Returns attribute constraints for each device type."""
            return {
                "camera": {
                    "power": ["on", "off"],
                    "recording": ["recording", "paused", "stopped"],
                    "motion_detection": ["motion_detected", "clear"]
                },
                "bulb": {
                    "power": ["on", "off"],
                    "brightness": {"type": "numeric", "min": 0, "max": 100}
                },
                "thermostat": {
                    "power": ["on", "off"],
                    "mode": ["heating", "cooling", "idle"],
                    "temperature": {"type": "numeric", "min": 32, "max": 104},
                    "target_temperature": {"type": "numeric", "min": 60, "max": 90}
                },
                "speaker": {
                    "power": ["on", "off"],
                    "playback_state": ["playing", "paused", "stopped"],
                    "volume": {"type": "numeric", "min": 0, "max": 100},
                    "mute": ["muted", "unmuted"]
                },
                "door_lock": {
                    "lock_state": ["locked", "unlocked"]
                },
                "motion_sensor": {
                    "motion_state": ["motion_detected", "clear"]
                },
                "temperature_sensor": {
                    "temperature": {"type": "numeric", "min": 32, "max": 104}
                },
                "humidity_sensor": {
                    "humidity": {"type": "numeric", "min": 0, "max": 100}
                },
                "light_sensor": {
                    "brightness_level": {"type": "numeric", "min": 0, "max": 65535}
                },
                "door_sensor": {
                    "door_state": ["open", "closed"]
                },
                "water_leak_sensor": {
                    "leak_state": ["leak_detected", "no_leak"]
                },
                "smoke_detector_sensor": {
                    "smoke_state": ["smoke_detected", "no_smoke", "alarm_triggered"]
                },
                "power_outlet": {
                    "power": ["on", "off"],
                    "power_consumption": {"type": "numeric", "min": 0, "max": 3680}
                },
                "air_conditioner": {
                    "power": ["on", "off"],
                    "mode": ["cooling", "idle"],
                    "temperature": {"type": "numeric", "min": 32, "max": 104},
                    "target_temperature": {"type": "numeric", "min": 60, "max": 85}
                }
            }

        def validate_device_attributes(device_type: str, attributes: Dict[str, Any]) -> Optional[str]:
            """Validate device attributes against constraints. Returns error message or None."""
            constraints = get_device_attribute_constraints()
            
            if device_type not in constraints:
                return f"Unknown device type: {device_type}"
            
            device_constraints = constraints[device_type]
            
            for attr_name, attr_config in attributes.items():
                # Extract value and comparison operator
                if isinstance(attr_config, dict):
                    attr_value = attr_config.get("value")
                else:
                    attr_value = attr_config
                
                if attr_name not in device_constraints:
                    return f"Invalid attribute '{attr_name}' for device type '{device_type}'. Valid attributes: {', '.join(device_constraints.keys())}"
                
                constraint = device_constraints[attr_name]
                
                # Check if constraint is a list of allowed values
                if isinstance(constraint, list):
                    if str(attr_value) not in constraint:
                        return f"Invalid value '{attr_value}' for attribute '{attr_name}'. Must be one of: {', '.join(constraint)}"
                
                # Check if constraint is a numeric range
                elif isinstance(constraint, dict) and constraint.get("type") == "numeric":
                    try:
                        numeric_value = float(attr_value)
                        min_val = constraint.get("min")
                        max_val = constraint.get("max")
                        if not (min_val <= numeric_value <= max_val):
                            return f"Value {numeric_value} for attribute '{attr_name}' must be between {min_val} and {max_val}"
                    except (ValueError, TypeError):
                        return f"Attribute '{attr_name}' must be a numeric value"
            
            return None

        timestamp = "2025-12-19T23:59:00"
        routine_triggers = data.get("routine_triggers", {})
        routines = data.get("routines", {})
        routine_schedules = data.get("routine_schedules", {})
        devices = data.get("devices", {})
        routine_trigger_attributes = data.get("routine_trigger_attributes", {})

        # Validate routine exists
        if routine_id not in routines:
            return json.dumps({
                "success": False,
                "error": f"Routine with ID '{routine_id}' not found"
            })

        # Get the routine's home_id for cross-home validation
        routine_home_id = routines[routine_id].get("home_id")

        # Validate trigger_type
        valid_trigger_types = ["time_based", "solar_event", "device_state", "manual"]
        if trigger_type not in valid_trigger_types:
            return json.dumps({
                "success": False,
                "error": f"Invalid trigger_type. Must be one of: {', '.join(valid_trigger_types)}"
            })

        # Validate trigger type specific requirements
        if trigger_type == "time_based":
            if not routine_schedule_id:
                return json.dumps({
                    "success": False,
                    "error": "routine_schedule_id is required for time_based trigger"
                })
            if routine_schedule_id not in routine_schedules:
                return json.dumps({
                    "success": False,
                    "error": f"Schedule with ID '{routine_schedule_id}' not found"
                })
            
            # Validate that the schedule belongs to the specified routine
            schedule_routine_id = routine_schedules[routine_schedule_id].get("routine_id")
            print(schedule_routine_id)
            print(routine_id)
            if schedule_routine_id != routine_id:
                return json.dumps({
                    "success": False,
                    "error": f"Schedule with ID '{routine_schedule_id}' does not belong to routine '{routine_id}'"
                })

        if trigger_type == "solar_event":
            if not solar_event:
                return json.dumps({
                    "success": False,
                    "error": "solar_event is required for solar_event trigger"
                })
            valid_solar_events = ["sunrise", "sunset"]
            if solar_event not in valid_solar_events:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid solar_event. Must be one of: {', '.join(valid_solar_events)}"
                })

        if trigger_type == "device_state":
            if not device_id:
                return json.dumps({
                    "success": False,
                    "error": "device_id is required for device_state trigger"
                })
            if device_id not in devices:
                return json.dumps({
                    "success": False,
                    "error": f"Device with ID '{device_id}' not found"
                })
            
            # Validate that the device belongs to the same home as the routine
            device_home_id = devices[device_id].get("home_id")
            if device_home_id != routine_home_id:
                return json.dumps({
                    "success": False,
                    "error": f"Device with ID '{device_id}' belongs to a different home than routine '{routine_id}'"
                })
            
            if not trigger_attributes:
                return json.dumps({
                    "success": False,
                    "error": "trigger_attributes are required for device_state trigger"
                })
            
            # Validate device attributes
            device_type = devices[device_id].get("device_type")
            validation_error = validate_device_attributes(device_type, trigger_attributes)
            if validation_error:
                return json.dumps({
                    "success": False,
                    "error": validation_error
                })

        # Generate new trigger ID
        new_trigger_id = generate_id(routine_triggers)

        # Create new trigger record
        new_trigger = {
            "trigger_id": new_trigger_id,
            "routine_id": routine_id,
            "trigger_type": trigger_type,
            "routine_schedule_id": routine_schedule_id,
            "solar_event": solar_event,
            "device_id": device_id,
            "created_at": timestamp,
            "updated_at": timestamp
        }

        routine_triggers[new_trigger_id] = new_trigger

        # Create trigger attributes if provided (for device_state trigger)
        created_attributes = []
        if trigger_attributes and trigger_type == "device_state":
            for attr_name, attr_config in trigger_attributes.items():
                attr_id = generate_id(routine_trigger_attributes)
                
                # Extract attribute value and comparison operator
                attr_value = attr_config.get("value") if isinstance(attr_config, dict) else attr_config
                comparison_operator = attr_config.get("comparison_operator") if isinstance(attr_config, dict) else None
                
                # Validate comparison operator if provided
                if comparison_operator:
                    valid_operators = ["equals", "greater_than", "less_than", "greater_equal", "less_equal"]
                    if comparison_operator not in valid_operators:
                        return json.dumps({
                            "success": False,
                            "error": f"Invalid comparison_operator. Must be one of: {', '.join(valid_operators)}"
                        })
                
                new_attribute = {
                    "attribute_id": attr_id,
                    "trigger_id": new_trigger_id,
                    "attribute_name": attr_name,
                    "attribute_value": str(attr_value),
                    "comparison_operator": comparison_operator,
                    "created_at": timestamp
                }
                routine_trigger_attributes[attr_id] = new_attribute
                created_attributes.append(new_attribute)

        result = {
            "success": True,
            "trigger_id": new_trigger_id,
            "trigger_data": new_trigger
        }
        
        if created_attributes:
            result["trigger_attributes"] = created_attributes

        return json.dumps(result)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "trigger_routine",
                "description": "Create a trigger for a routine. Defines when and under what conditions a routine should be executed. Supports time-based (scheduled), solar event (sunrise/sunset), device state changes, and manual triggers. Device attributes are validated based on device type: camera (power: on/off, recording: recording/paused/stopped, motion_detection: motion_detected/clear), bulb (power: on/off, brightness: 0-100), thermostat (power: on/off, mode: heating/cooling/idle, temperature: 32-104, target_temperature: 60-90), speaker (power: on/off, playback_state: playing/paused/stopped, volume: 0-100, mute: muted/unmuted), door_lock (lock_state: locked/unlocked), motion_sensor (motion_state: motion_detected/clear), temperature_sensor (temperature: 32-104), humidity_sensor (humidity: 0-100), light_sensor (brightness_level: 0-65535), door_sensor (door_state: open/closed), water_leak_sensor (leak_state: leak_detected/no_leak), smoke_detector_sensor (smoke_state: smoke_detected/no_smoke/alarm_triggered), power_outlet (power: on/off, power_consumption: 0-3680), air_conditioner (power: on/off, mode: cooling/idle, temperature: 32-104, target_temperature: 60-85).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "routine_id": {
                            "type": "string",
                            "description": "The ID of the routine to trigger"
                        },
                        "trigger_type": {
                            "type": "string",
                            "description": "Type of trigger: 'time_based' (scheduled), 'solar_event' (sunrise/sunset), 'device_state' (device condition), 'manual' (user-initiated)"
                        },
                        "routine_schedule_id": {
                            "type": "string",
                            "description": "Schedule ID (required for time_based trigger type)"
                        },
                        "solar_event": {
                            "type": "string",
                            "description": "Solar event type: 'sunrise' or 'sunset' (required for solar_event trigger type)"
                        },
                        "device_id": {
                            "type": "string",
                            "description": "Device ID to monitor (required for device_state trigger type)"
                        },
                        "trigger_attributes": {
                            "type": "object",
                            "description": "Device state attributes to monitor (required for device_state trigger type). Attributes and values must match the device type constraints. SYNTAX: {\"attribute_name\": \"value\"} or {\"attribute_name\": {\"value\": \"val\", \"comparison_operator\": \"equals\"}}. Comparison operators: 'equals', 'greater_than', 'less_than', 'greater_equal', 'less_equal'"
                        }
                    },
                    "required": ["routine_id", "trigger_type"]
                }
            }
        }