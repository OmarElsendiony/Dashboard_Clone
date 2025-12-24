import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class AddRoutineTrigger(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        trigger_type: str,
        trigger_attributes: Dict[str, Any],
        routine_id: Optional[str] = None,
        routine_name: Optional[str] = None,
        schedule_id: Optional[str] = None,
        solar_event: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        def generate_id(table: Dict[str, Any]) -> int:
            return max([int(k) for k in table.keys()], default=0) + 1

        # Implement your tool logic here
        routines = data.get("routines", {})
        if routine_name and not routine_id:
            for rid, routine in routines.items():
                if (
                    routine.get("routine_name").strip().lower()
                    == routine_name.strip().lower()
                ):
                    routine_id = rid
                    break
            if not routine_id:
                return json.dumps(
                    {"success": False, "error": "Routine ID or name required"}
                )
        routine = routines.get(routine_id)
        if not routine:
            return json.dumps({"success": False, "error": "Routine not found"})
        routine_schedules = data.get("routine_schedules", {})
        schedule = routine_schedules.get(schedule_id)
        if schedule_id and not schedule:
            return json.dumps({"success": False, "error": "Schedule not found"})

        if solar_event and solar_event not in ["sunrise", "sunset"]:
            return json.dumps({"success": False, "error": "Invalid solar event"})
        if device_id and device_id not in data.get("devices", {}):
            return json.dumps({"success": False, "error": "Device not found"})
        if trigger_type not in ["time_based", "solar_event", "device_state", "manual"]:
            return json.dumps({"success": False, "error": "Invalid trigger type"})
        routine_tiggers = data.get("routine_triggers", {})
        next_trigger_id = generate_id(routine_tiggers)
        timestamp = "2025-12-19T23:59:00"
        trigger = {
            "trigger_id": str(next_trigger_id),
            "routine_id": routine_id,
            "routine_schedule_id": schedule_id,
            "trigger_type": trigger_type,
            "solar_event": solar_event,
            "device_id": device_id,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        routine_tiggers[str(next_trigger_id)] = trigger
        data["routine_triggers"] = routine_tiggers
        routine_trigger_attribute = None
        if trigger_attributes:
            routine_trigger_attributes = data.get("routine_trigger_attributes", {})
            next_attr_id = generate_id(routine_trigger_attributes)
            routine_trigger_attribute = {
                "attribute_id": str(next_attr_id),
                "routine_id": routine_id,
                "trigger_id": str(next_trigger_id),
                "attribute_name": trigger_attributes.get("attribute_name"),
                "attribute_value": trigger_attributes.get("attribute_value"),
                "comparison_operator": trigger_attributes.get("comparison_operator"),
                "created_at": timestamp,
                "updated_at": timestamp,
            }
            routine_trigger_attributes[str(next_attr_id)] = routine_trigger_attribute
            data["routine_trigger_attributes"] = routine_trigger_attributes
        return json.dumps(
            {
                "success": True,
                "routine_trigger": trigger,
                "attributes": routine_trigger_attribute if trigger_attributes else None,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_routine_trigger",
                "description": "Add a trigger to a specified routine in a smart home system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        # Define your parameters here
                        "routine_id": {
                            "type": "string",
                            "description": "The ID of the routine to which the trigger will be added.",
                        },
                        "routine_name": {
                            "type": "string",
                            "description": "The name of the routine to which the trigger will be added (used if routine_id is not provided).",
                        },
                        "trigger_type": {
                            "type": "string",
                            "description": "The type of trigger to be added (e.g., time_based, solar_event, device_state, manual).",
                        },
                        "trigger_attributes": {
                            "type": "object",
                            "description": "A dictionary of attributes specific to the trigger type. Including attribute_name, attribute_value, comparison_operator.",
                        },
                        "schedule_id": {
                            "type": "string",
                            "description": "The ID of the schedule associated with the trigger, if applicable.",
                        },
                        "solar_event": {
                            "type": "string",
                            "description": "The solar event associated with the trigger (e.g., sunrise, sunset), if applicable.",
                        },
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device associated with the trigger, if applicable.",
                        },
                    },
                    "required": ["trigger_type", "trigger_attributes"],
                },
            },
        }
