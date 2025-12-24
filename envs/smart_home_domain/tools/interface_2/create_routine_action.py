import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateRoutineAction(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        routine_id: str,
        action_type: str,
        target_device_id: Optional[str] = None,
        target_scene_id: Optional[str] = None,
        target_notification_id: Optional[str] = None,
        device_attributes: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create an action for a routine.
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
            
            for attr_name, attr_value in attributes.items():
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
        routine_actions = data.get("routine_actions", {})
        routines = data.get("routines", {})
        devices = data.get("devices", {})
        scenes = data.get("scenes", {})
        notifications = data.get("notifications", {})
        routine_action_attributes = data.get("routine_action_attributes", {})

        # Validate routine exists
        if routine_id not in routines:
            return json.dumps({
                "success": False,
                "error": f"Routine with ID '{routine_id}' not found"
            })

        # Get the routine's home_id for cross-home validation
        routine_home_id = routines[routine_id].get("home_id")

        # Validate action_type
        valid_action_types = ["device_control", "scene_activation", "notification"]
        if action_type not in valid_action_types:
            return json.dumps({
                "success": False,
                "error": f"Invalid action_type. Must be one of: {', '.join(valid_action_types)}"
            })

        # Validate action type specific requirements
        if action_type == "device_control":
            if not target_device_id:
                return json.dumps({
                    "success": False,
                    "error": "target_device_id is required for device_control action"
                })
            if target_device_id not in devices:
                return json.dumps({
                    "success": False,
                    "error": f"Device with ID '{target_device_id}' not found"
                })
            
            # Validate that the device belongs to the same home as the routine
            device_home_id = devices[target_device_id].get("home_id")
            if device_home_id != routine_home_id:
                return json.dumps({
                    "success": False,
                    "error": f"Device with ID '{target_device_id}' belongs to a different home than routine '{routine_id}'"
                })
            
            if not device_attributes:
                return json.dumps({
                    "success": False,
                    "error": "device_attributes are required for device_control action"
                })
            
            # Validate device attributes
            device_type = devices[target_device_id].get("device_type")
            validation_error = validate_device_attributes(device_type, device_attributes)
            if validation_error:
                return json.dumps({
                    "success": False,
                    "error": validation_error
                })

        if action_type == "scene_activation":
            if not target_scene_id:
                return json.dumps({
                    "success": False,
                    "error": "target_scene_id is required for scene_activation action"
                })
            if target_scene_id not in scenes:
                return json.dumps({
                    "success": False,
                    "error": f"Scene with ID '{target_scene_id}' not found"
                })
            
            # Validate that the scene belongs to the same home as the routine
            scene_home_id = scenes[target_scene_id].get("home_id")
            if scene_home_id != routine_home_id:
                return json.dumps({
                    "success": False,
                    "error": f"Scene with ID '{target_scene_id}' belongs to a different home than routine '{routine_id}'"
                })

        if action_type == "notification":
            if not target_notification_id:
                return json.dumps({
                    "success": False,
                    "error": "target_notification_id is required for notification action"
                })
            if target_notification_id not in notifications:
                return json.dumps({
                    "success": False,
                    "error": f"Notification with ID '{target_notification_id}' not found"
                })
            
            # Validate that the notification belongs to the same home as the routine (if home_id is set)
            notification_home_id = notifications[target_notification_id].get("home_id")
            if notification_home_id is not None and notification_home_id != routine_home_id:
                return json.dumps({
                    "success": False,
                    "error": f"Notification with ID '{target_notification_id}' belongs to a different home than routine '{routine_id}'"
                })

        # Generate new action ID
        new_action_id = generate_id(routine_actions)

        # Create new action record
        new_action = {
            "action_id": new_action_id,
            "routine_id": routine_id,
            "action_type": action_type,
            "target_device_id": target_device_id,
            "target_scene_id": target_scene_id,
            "target_notification_id": target_notification_id,
            "created_at": timestamp,
            "updated_at": timestamp
        }

        routine_actions[new_action_id] = new_action

        # Create action attributes if provided (for device_control action)
        created_attributes = []
        if device_attributes and action_type == "device_control":
            for attr_name, attr_value in device_attributes.items():
                attr_id = generate_id(routine_action_attributes)
                new_attribute = {
                    "attribute_id": attr_id,
                    "action_id": new_action_id,
                    "attribute_name": attr_name,
                    "attribute_value": str(attr_value),
                    "created_at": timestamp
                }
                routine_action_attributes[attr_id] = new_attribute
                created_attributes.append(new_attribute)

        result = {
            "success": True,
            "action_id": new_action_id,
            "action_data": new_action
        }
        
        if created_attributes:
            result["action_attributes"] = created_attributes

        return json.dumps(result)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_routine_action",
                "description": "Create an action for a routine. Defines what should happen when the routine is triggered. Supports device control (controlling smart devices), scene activation (activating predefined scenes), and notifications (sending alerts). Device attributes are validated based on device type: camera (power: on/off, recording: recording/paused/stopped, motion_detection: motion_detected/clear), bulb (power: on/off, brightness: 0-100), thermostat (power: on/off, mode: heating/cooling/idle, temperature: 32-104, target_temperature: 60-90), speaker (power: on/off, playback_state: playing/paused/stopped, volume: 0-100, mute: muted/unmuted), door_lock (lock_state: locked/unlocked), motion_sensor (motion_state: motion_detected/clear), temperature_sensor (temperature: 32-104), humidity_sensor (humidity: 0-100), light_sensor (brightness_level: 0-65535), door_sensor (door_state: open/closed), water_leak_sensor (leak_state: leak_detected/no_leak), smoke_detector_sensor (smoke_state: smoke_detected/no_smoke/alarm_triggered), power_outlet (power: on/off, power_consumption: 0-3680), air_conditioner (power: on/off, mode: cooling/idle, temperature: 32-104, target_temperature: 60-85).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "routine_id": {
                            "type": "string",
                            "description": "The ID of the routine to add the action to"
                        },
                        "action_type": {
                            "type": "string",
                            "description": "Type of action: 'device_control' (control a device), 'scene_activation' (activate a scene), 'notification' (send notification)"
                        },
                        "target_device_id": {
                            "type": "string",
                            "description": "Device ID to control (required for device_control action type)"
                        },
                        "target_scene_id": {
                            "type": "string",
                            "description": "Scene ID to activate (required for scene_activation action type)"
                        },
                        "target_notification_id": {
                            "type": "string",
                            "description": "Notification ID to send (required for notification action type)"
                        },
                        "device_attributes": {
                            "type": "object",
                            "description": "Device state attributes to set (required for device_control action type). Attributes and values must match the device type constraints. SYNTAX: {\"attribute_name\": \"value\"}. Example: {\"power\": \"on\", \"brightness\": \"75\"}"
                        }
                    },
                    "required": ["routine_id", "action_type"]
                }
            }
        }