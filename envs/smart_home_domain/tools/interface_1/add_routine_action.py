import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class AddRoutineAction(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action_type: str,
        routine_id: str,
        action_parameters: Optional[Dict[str, Any]] = None,
        action_attributes: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        def generate_id(table: Dict[str, Any]) -> int:
            return max([int(k) for k in table.keys()], default=0) + 1

        routines = data.get("routines", {})

        routine = routines.get(routine_id)
        if not routine:
            return json.dumps({"success": False, "error": "Routine not found"})
        if action_type not in ["device_control", "notification"]:
            return json.dumps({"success": False, "error": "Invalid action type"})
        routine_actions = data.get("routine_actions", {})
        next_action_id = generate_id(routine_actions)
        timestamp = "2025-12-19T23:59:00"
        action = {
            "action_id": str(next_action_id),
            "routine_id": routine_id,
            "action_type": action_type,
            "target_device_id": (
                action_parameters.get("target_device_id") if action_parameters else None
            ),
            "target_notification_id": (
                action_parameters.get("target_notification_id")
                if action_parameters
                else None
            ),
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        full_action = action.copy()
        full_action["target_scene_id"] = None
        routine_actions[str(next_action_id)] = full_action
        data["routine_actions"] = routine_actions
        routine_action_attribute = None
        if action_attributes:
            routine_action_attributes = data.get("routine_action_attributes", {})
            next_attr_id = generate_id(routine_action_attributes)
            routine_action_attribute = {
                "action_id": str(next_action_id),
                "attribute_name": action_attributes.get("attribute_name"),
                "attribute_value": action_attributes.get("attribute_value"),
                "created_at": timestamp,
                "updated_at": timestamp,
            }
            routine_action_attributes[str(next_attr_id)] = routine_action_attribute
            data["routine_action_attributes"] = routine_action_attributes
        return json.dumps(
            {
                "success": True,
                "routine_action": action,
                "attributes": routine_action_attribute if action_attributes else None,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_routine_action",
                "description": "Add an action to a specified routine in a smart home system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action_type": {
                            "type": "string",
                            "description": "The type of action to be added (e.g., device_control, notification).",
                        },
                        "routine_id": {
                            "type": "string",
                            "description": "The ID of the routine to which the action will be added.",
                        },
                        "action_parameters": {
                            "type": "object",
                            "description": "A dictionary of parameters specific to the action type. Including target_device_id, target_notification_id.",
                        },
                        "action_attributes": {
                            "type": "object",
                            "description": "A dictionary of attributes specific to the action. Including attribute_name, attribute_value.",
                        },
                    },
                    "required": ["action_type", "routine_id"],
                },
            },
        }
