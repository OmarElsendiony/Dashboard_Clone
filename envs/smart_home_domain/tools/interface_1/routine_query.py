import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class RoutineQuery(Tool):
    """
    Query a routine by home_id and routine_name.
    Returns detailed information about the routine including triggers, actions, and schedules.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        routine_name: str
    ) -> str:
        """
        Query a routine by home_id and routine_name.
        
        Args:
            data: The data dictionary containing routines, triggers, actions, and schedules
            home_id: The ID of the home
            routine_name: The name of the routine to query
            
        Returns:
            JSON string with success status and routine details
        """
        # Basic input validation
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        homes_dict = data.get("homes", {})
        if not isinstance(homes_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid homes container: expected dict at data['homes']"
            })

        routines_dict = data.get("routines", {})
        if not isinstance(routines_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid routines container: expected dict at data['routines']"
            })

        routine_triggers_dict = data.get("routine_triggers", {})
        if not isinstance(routine_triggers_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid routine_triggers container: expected dict at data['routine_triggers']"
            })

        routine_actions_dict = data.get("routine_actions", {})
        if not isinstance(routine_actions_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid routine_actions container: expected dict at data['routine_actions']"
            })

        routine_schedules_dict = data.get("routine_schedules", {})
        if not isinstance(routine_schedules_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid routine_schedules container: expected dict at data['routine_schedules']"
            })

        # Validate required fields
        if home_id is None:
            return json.dumps({"success": False, "error": "home_id is required"})

        if routine_name is None or not routine_name.strip():
            return json.dumps({
                "success": False,
                "error": "routine_name is required and cannot be empty"
            })

        # Convert to strings for consistent comparison
        home_id_str = str(home_id)
        routine_name_str = str(routine_name).strip()

        # Validate home exists
        if home_id_str not in homes_dict:
            return json.dumps({
                "success": False,
                "error": f"Home not found: '{home_id_str}'"
            })

        # Find routine by home_id and routine_name
        routine_id = None
        routine_data = None
        for rid, routine in routines_dict.items():
            if isinstance(routine, dict) and str(routine.get("home_id")) == home_id_str and routine.get("routine_name") == routine_name_str:
                routine_id = rid
                routine_data = dict(routine)
                break

        if routine_id is None:
            return json.dumps({
                "success": False,
                "error": f"Routine not found with name '{routine_name_str}' in home_id '{home_id_str}'"
            })

        # Get all triggers for this routine
        triggers = []
        for trigger_id, trigger in routine_triggers_dict.items():
            if isinstance(trigger, dict) and str(trigger.get("routine_id")) == routine_id:
                trigger_data = {
                    "trigger_id": trigger_id,
                    **trigger
                }
                
                # If it's a time_based trigger, include schedule details
                if trigger.get("trigger_type") == "time_based" and trigger.get("routine_schedule_id"):
                    schedule_id = str(trigger.get("routine_schedule_id"))
                    if schedule_id in routine_schedules_dict:
                        trigger_data["schedule"] = routine_schedules_dict[schedule_id]
                
                triggers.append(trigger_data)

        # Get all actions for this routine
        actions = []
        for action_id, action in routine_actions_dict.items():
            if isinstance(action, dict) and str(action.get("routine_id")) == routine_id:
                actions.append({
                    "action_id": action_id,
                    **action
                })

        # Sort triggers and actions by their IDs for consistent ordering
        triggers.sort(key=lambda x: int(x["trigger_id"]))
        actions.sort(key=lambda x: int(x["action_id"]))

        return json.dumps({
            "success": True,
            "routine": {
                "routine_id": routine_id,
                **routine_data,
                "triggers": triggers,
                "actions": actions,
                "trigger_count": len(triggers),
                "action_count": len(actions)
            }
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """
        Tool schema for function-calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "routine_query",
                "description": (
                    "Query a routine by home_id and routine_name. "
                    "Returns detailed information about the routine including its configuration, triggers, actions, and schedules. "
                    "Triggers can be time_based, device_state, manual, or solar_event. "
                    "Actions can be device_control, scene_activation, or notification. "
                    "For time_based triggers, schedule details are included."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "The ID of the home (required)."
                        },
                        "routine_name": {
                            "type": "string",
                            "description": "The name of the routine to query (required)."
                        }
                    },
                    "required": ["home_id", "routine_name"],
                },
            },
        }

