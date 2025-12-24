import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateSchedule(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        schedule_object: Dict[str, Any],
        routine_id: Optional[str] = None,
        routine_name: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        # Implement your tool logic here
        def generate_id(table: Dict[str, Any]) -> int:
            return max([int(k) for k in table.keys()], default=0) + 1

        routines = data.get("routines", {})
        if routine_name and not routine_id:
            for rid, routine in routines.items():
                if (
                    routine.get("routine_name").strip().lower()
                    == routine_name.strip().lower()
                ):
                    routine_id = rid
                    break
        routine = routines.get(routine_id)
        if not routine:
            return json.dumps({"success": False, "error": "Routine not found"})
        if not schedule_object:
            return json.dumps(
                {"success": False, "error": "Schedule object is required"}
            )
        # if existing schedule is found for the routine, update it
        routine_schedules = data.get("routine_schedules", {})
        timestamp = "2025-12-19T23:59:00"
        trusy_map = set([True, "true", "True", 1, "1"])
        for schedule_id, schedule in routine_schedules.items():
            if schedule.get("routine_id") == routine_id:
                # Update existing schedule
                updated_schedule = {
                    "schedule_id": schedule_id,
                    "routine_id": routine_id,
                    "on_monday": schedule_object.get("on_monday", False) in trusy_map,
                    "on_tuesday": schedule_object.get("on_tuesday", False) in trusy_map,
                    "on_wednesday": schedule_object.get("on_wednesday", False)
                    in trusy_map,
                    "on_thursday": schedule_object.get("on_thursday", False)
                    in trusy_map,
                    "on_friday": schedule_object.get("on_friday", False) in trusy_map,
                    "on_saturday": schedule_object.get("on_saturday", False)
                    in trusy_map,
                    "onset_time": None,
                    "on_sunday": schedule_object.get("on_sunday", False) in trusy_map,
                    "created_at": timestamp,
                    "updated_at": timestamp,
                }
                routine_schedules[schedule_id] = updated_schedule
                data["routine_schedules"] = routine_schedules
                return json.dumps(
                    {"success": True, "routine_schedule": updated_schedule}
                )

        routine_schedules = data.get("routine_schedules", {})
        next_schedule_id = generate_id(routine_schedules)
        trusy_map = set([True, "true", "True", 1, "1"])

        schedule = {
            "schedule_id": str(next_schedule_id),
            "routine_id": routine_id,
            "on_monday": schedule_object.get("on_monday", False) in trusy_map,
            "on_tuesday": schedule_object.get("on_tuesday", False) in trusy_map,
            "on_wednesday": schedule_object.get("on_wednesday", False) in trusy_map,
            "on_thursday": schedule_object.get("on_thursday", False) in trusy_map,
            "on_friday": schedule_object.get("on_friday", False) in trusy_map,
            "on_saturday": schedule_object.get("on_saturday", False) in trusy_map,
            "on_sunday": schedule_object.get("on_sunday", False) in trusy_map,
            "onset_time": None,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        routine_schedules[str(next_schedule_id)] = schedule
        data["routine_schedules"] = routine_schedules
        return json.dumps({"success": True, "routine_schedule": schedule})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_schedule",
                "description": "Create a schedule for a specified routine in a smart home system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "routine_id": {
                            "type": "string",
                            "description": "The ID of the routine to create a schedule for.",
                        },
                        "routine_name": {
                            "type": "string",
                            "description": "The name of the routine to create a schedule for.",
                        },
                        "schedule_object": {
                            "type": "object",
                            "description": "An object defining the schedule details, such as days of the week.E.g. {'on_monday': 'true', 'on_tuesday': 'false'}.",
                        },
                    },
                    "required": ["schedule_object"],
                },
            },
        }
