import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class UpdateRoutineAction(Tool):
    """
    Update a routine action's attributes.
    - Requires routine_id, action_id, and updates dict.
    - Validates that routine and action exist.
    - Updates the 'updated_at' timestamp automatically.
    - Cannot update action_id, routine_id, or created_at.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        routine_id: str,
        action_id: str,
        updates: Dict[str, Any]
    ) -> str:
        """
        Update a routine action's attributes.
        
        Args:
            data: The data dictionary containing routines and routine_actions
            routine_id: The ID of the routine
            action_id: The ID of the action to update
            updates: Dictionary of fields to update
            
        Returns:
            JSON string with success status and updated action information
        """
        # Basic input validation
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        routines_dict = data.get("routines", {})
        if not isinstance(routines_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid routines container: expected dict at data['routines']"
            })

        routine_actions_dict = data.get("routine_actions", {})
        if not isinstance(routine_actions_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid routine_actions container: expected dict at data['routine_actions']"
            })

        devices_dict = data.get("devices", {})
        if not isinstance(devices_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid devices container: expected dict at data['devices']"
            })

        scenes_dict = data.get("scenes", {})
        if not isinstance(scenes_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid scenes container: expected dict at data['scenes']"
            })

        notifications_dict = data.get("notifications", {})
        if not isinstance(notifications_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid notifications container: expected dict at data['notifications']"
            })

        # Validate required fields
        if routine_id is None:
            return json.dumps({"success": False, "error": "routine_id is required"})

        if action_id is None:
            return json.dumps({"success": False, "error": "action_id is required"})

        if not isinstance(updates, dict):
            return json.dumps({
                "success": False,
                "error": "updates must be a dictionary"
            })

        if not updates:
            return json.dumps({
                "success": False,
                "error": "updates dictionary cannot be empty"
            })

        # Convert to strings for consistent comparison
        routine_id_str = str(routine_id)
        action_id_str = str(action_id)

        # Validate routine exists
        if routine_id_str not in routines_dict:
            return json.dumps({
                "success": False,
                "error": f"Routine not found: '{routine_id_str}'"
            })

        # Validate action exists
        if action_id_str not in routine_actions_dict:
            return json.dumps({
                "success": False,
                "error": f"Action not found: '{action_id_str}'"
            })

        action_data = routine_actions_dict[action_id_str]

        # Validate action belongs to the specified routine
        if str(action_data.get("routine_id")) != routine_id_str:
            return json.dumps({
                "success": False,
                "error": f"Action '{action_id_str}' does not belong to routine '{routine_id_str}'"
            })

        # Validate that protected fields are not in updates
        protected_fields = ["action_id", "routine_id", "created_at"]
        for field in protected_fields:
            if field in updates:
                return json.dumps({
                    "success": False,
                    "error": f"Cannot update protected field: '{field}'"
                })

        # Valid action types
        valid_action_types = ["device_control", "scene_activation", "notification"]

        # Validate updates values
        for key, value in updates.items():
            if key == "action_type":
                if value not in valid_action_types:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid action_type: '{value}'. Must be one of {valid_action_types}"
                    })
            
            elif key == "target_device_id":
                if value is not None and str(value) not in devices_dict:
                    return json.dumps({
                        "success": False,
                        "error": f"Device not found: '{value}'"
                    })
            
            elif key == "target_scene_id":
                if value is not None and str(value) not in scenes_dict:
                    return json.dumps({
                        "success": False,
                        "error": f"Scene not found: '{value}'"
                    })
            
            elif key == "target_notification_id":
                if value is not None and str(value) not in notifications_dict:
                    return json.dumps({
                        "success": False,
                        "error": f"Notification not found: '{value}'"
                    })
            
            elif key not in ["action_type", "target_device_id", "target_scene_id", "target_notification_id"]:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid update field: '{key}'. Allowed fields: action_type, target_device_id, target_scene_id, target_notification_id"
                })

        # Validate action_type consistency with targets
        new_action_type = updates.get("action_type", action_data.get("action_type"))
        
        # Determine final target values after update
        final_target_device_id = updates.get("target_device_id", action_data.get("target_device_id")) if "target_device_id" in updates else action_data.get("target_device_id")
        final_target_scene_id = updates.get("target_scene_id", action_data.get("target_scene_id")) if "target_scene_id" in updates else action_data.get("target_scene_id")
        final_target_notification_id = updates.get("target_notification_id", action_data.get("target_notification_id")) if "target_notification_id" in updates else action_data.get("target_notification_id")

        # Validate consistency between action_type and targets
        if new_action_type == "device_control" and final_target_device_id is None:
            return json.dumps({
                "success": False,
                "error": "action_type 'device_control' requires target_device_id to be set"
            })
        
        if new_action_type == "scene_activation" and final_target_scene_id is None:
            return json.dumps({
                "success": False,
                "error": "action_type 'scene_activation' requires target_scene_id to be set"
            })
        
        if new_action_type == "notification" and final_target_notification_id is None:
            return json.dumps({
                "success": False,
                "error": "action_type 'notification' requires target_notification_id to be set"
            })

        # Apply updates
        current_time = "2025-12-19T23:59:00"
        
        for key, value in updates.items():
            action_data[key] = value

        # Always update timestamp
        action_data["updated_at"] = current_time

        return json.dumps({
            "success": True,
            "message": f"Action '{action_id_str}' of routine '{routine_id_str}' updated successfully",
            "action": action_data
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_routine_action",
                "description": (
                    "Update a routine action's attributes. "
                    "Requires routine_id, action_id, and updates dictionary. "
                    "Validates that routine and action exist. "
                    "Updates the 'updated_at' timestamp automatically. "
                    "Allowed update fields: action_type, target_device_id, target_scene_id, target_notification_id. "
                    "Cannot update action_id, routine_id, or created_at. "
                    "Valid action types: device_control, scene_activation, notification. "
                    "Ensures consistency between action_type and target fields."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "routine_id": {
                            "type": "string",
                            "description": "The ID of the routine (required)."
                        },
                        "action_id": {
                            "type": "string",
                            "description": "The ID of the action to update (required)."
                        },
                        "updates": {
                            "type": "object",
                            "description": "Dictionary of fields to update. Allowed fields: action_type, target_device_id, target_scene_id, target_notification_id.",
                            "additionalProperties": True
                        }
                    },
                    "required": ["routine_id", "action_id", "updates"],
                },
            },
        }

