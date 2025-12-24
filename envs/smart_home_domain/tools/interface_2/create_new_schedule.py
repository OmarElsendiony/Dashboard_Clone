import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class CreateNewSchedule(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        routine_id: str,
        on_monday: bool = False,
        on_tuesday: bool = False,
        on_wednesday: bool = False,
        on_thursday: bool = False,
        on_friday: bool = False,
        on_saturday: bool = False,
        on_sunday: bool = False,
        onset_time: Optional[str] = None,
    ) -> str:
        """
        Create a new schedule for a routine.
        """
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        timestamp = "2025-10-01T00:00:00"
        routine_schedules = data.get("routine_schedules", {})
        routines = data.get("routines", {})

        # Validate routine exists
        if routine_id not in routines:
            return json.dumps({
                "success": False,
                "error": f"Routine with ID '{routine_id}' not found"
            })

        # Validate that at least one day is selected
        days_selected = any([on_monday, on_tuesday, on_wednesday, on_thursday, on_friday, on_saturday, on_sunday])
        if not days_selected:
            return json.dumps({
                "success": False,
                "error": "At least one day must be selected for the schedule"
            })

        # Validate onset_time format if provided (HH:MM:SS)
        if onset_time:
            try:
                time_parts = onset_time.split(':')
                if len(time_parts) != 3:
                    return json.dumps({
                        "success": False,
                        "error": "Invalid onset_time format. Use HH:MM:SS"
                    })
                hours, minutes, seconds = map(int, time_parts)
                if not (0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59):
                    return json.dumps({
                        "success": False,
                        "error": "Invalid onset_time values. Hours: 0-23, Minutes: 0-59, Seconds: 0-59"
                    })
            except ValueError:
                return json.dumps({
                    "success": False,
                    "error": "Invalid onset_time format. Use HH:MM:SS"
                })

        # Generate new schedule ID
        new_schedule_id = generate_id(routine_schedules)

        # Create new schedule record
        new_schedule = {
            "schedule_id": new_schedule_id,
            "routine_id": routine_id,
            "on_monday": on_monday,
            "on_tuesday": on_tuesday,
            "on_wednesday": on_wednesday,
            "on_thursday": on_thursday,
            "on_friday": on_friday,
            "on_saturday": on_saturday,
            "on_sunday": on_sunday,
            "onset_time": onset_time
        }

        routine_schedules[new_schedule_id] = new_schedule

        return json.dumps({
            "success": True,
            "schedule_id": new_schedule_id,
            "schedule_data": new_schedule
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_new_schedule",
                "description": "Create a new schedule for a routine. Defines which days of the week and at what time a routine should be triggered. At least one day must be selected.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "routine_id": {
                            "type": "string",
                            "description": "The ID of the routine to schedule"
                        },
                        "on_monday": {
                            "type": "boolean",
                            "description": "Run routine on Monday (True/False)"
                        },
                        "on_tuesday": {
                            "type": "boolean",
                            "description": "Run routine on Tuesday (True/False)"
                        },
                        "on_wednesday": {
                            "type": "boolean",
                            "description": "Run routine on Wednesday (True/False)"
                        },
                        "on_thursday": {
                            "type": "boolean",
                            "description": "Run routine on Thursday (True/False)"
                        },
                        "on_friday": {
                            "type": "boolean",
                            "description": "Run routine on Friday (True/False)"
                        },
                        "on_saturday": {
                            "type": "boolean",
                            "description": "Run routine on Saturday (True/False)"
                        },
                        "on_sunday": {
                            "type": "boolean",
                            "description": "Run routine on Sunday (True/False)"
                        },
                        "onset_time": {
                            "type": "string",
                            "description": "Time to trigger the routine in HH:MM:SS format (e.g., '14:30:00')"
                        }
                    },
                    "required": ["routine_id"]
                }
            }
        }
