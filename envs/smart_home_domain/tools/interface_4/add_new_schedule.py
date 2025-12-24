import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool
from datetime import datetime

class AddNewSchedule(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        automation_id: str,
        time: str,
        on_monday: bool = False,
        on_tuesday: bool = False,
        on_wednesday: bool = False,
        on_thursday: bool = False,
        on_friday: bool = False,
        on_saturday: bool = False,
        on_sunday: bool = False,
    ) -> str:
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

        routine_schedule_dict = data.get("routine_schedules", {})
        if not isinstance(routine_schedule_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid routine_schedules container: expected dict at data['routine_schedules']",
                }
            )

        # Type cast automation_id to string as requested
        if not automation_id:
            return json.dumps({"success": False, "error": "automation_id is required"})
        automation_id_str = str(automation_id).strip()

        # Check if automation exists
        if automation_id_str not in routines_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Automation with ID '{automation_id_str}' not found",
                }
            )

        # Validate boolean parameters
        day_params = {
            "on_monday": on_monday,
            "on_tuesday": on_tuesday,
            "on_wednesday": on_wednesday,
            "on_thursday": on_thursday,
            "on_friday": on_friday,
            "on_saturday": on_saturday,
            "on_sunday": on_sunday,
        }

        for param_name, param_value in day_params.items():
            if not isinstance(param_value, bool):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid {param_name}: must be a boolean value (True/False)",
                    }
                )

        # Ensure at least one day is selected
        if not any(day_params.values()):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one day must be selected for the schedule",
                }
            )

        # Validate time format
        time_str = str(time).strip()
        if not time_str:
            return json.dumps({"success": False, "error": "time parameter is required"})

        # Validate time format (HH:MM:SS)
        try:
            # Try parsing HH:MM:SS format
            if len(time_str.split(":")) == 3:
                datetime.strptime(time_str, "%H:%M:%S")
            else:
                raise ValueError("Invalid time format")
        except ValueError:
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid time format. Expected format: HH:MM:SS (24-hour format, e.g., '14:30:00')",
                }
            )

        # Generate unique schedule_id
        # Generate new IDs
        def generate_id(table: Dict[str, Any]) -> str:
            """Generates a new unique ID for a record."""
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        schedule_id = generate_id(routine_schedule_dict)

        # Create new schedule entry
        new_schedule = {
            "schedule_id": schedule_id,
            "routine_id": automation_id_str,
            "on_monday": on_monday,
            "on_tuesday": on_tuesday,
            "on_wednesday": on_wednesday,
            "on_thursday": on_thursday,
            "on_friday": on_friday,
            "on_saturday": on_saturday,
            "on_sunday": on_sunday,
            "onset_time": time_str,
        }

        # Add to data structure
        routine_schedule_dict[schedule_id] = new_schedule

        new_schedule_return = new_schedule.copy()
        new_schedule_return["automation_id"] = new_schedule_return.pop("routine_id")

        # Build human-readable days list for response
        selected_days = []
        day_names = {
            "on_monday": "Monday",
            "on_tuesday": "Tuesday",
            "on_wednesday": "Wednesday",
            "on_thursday": "Thursday",
            "on_friday": "Friday",
            "on_saturday": "Saturday",
            "on_sunday": "Sunday",
        }
        for param_name, is_selected in day_params.items():
            if is_selected:
                selected_days.append(day_names[param_name])

        return json.dumps(
            {
                "success": True,
                "schedule_id": schedule_id,
                "message": f"Schedule created successfully for automation '{automation_id_str}' on {', '.join(selected_days)} at {time_str}",
                "schedule": new_schedule,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_new_schedule",
                "description": (
                    "Create a new schedule for an automation. "
                    "Creates a schedule with specified days of the week and time. "
                    "The schedule determines when the automation should run. "
                    "At least one day must be selected. "
                    "Time must be in HH:MM:SS format (24-hour). "
                    "Returns the created schedule_id on success. "
                    "Returns an error if the automation doesn't exist or validation fails."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "automation_id": {
                            "type": "string",
                            "description": "The automation ID to create a schedule for.",
                        },
                        "on_monday": {
                            "type": "boolean",
                            "description": "Defualt False. Whether the schedule is active on Monday.",
                        },
                        "on_tuesday": {
                            "type": "boolean",
                            "description": "Default False. Whether the schedule is active on Tuesday.",
                        },
                        "on_wednesday": {
                            "type": "boolean",
                            "description": "Default False. Whether the schedule is active on Wednesday.",
                        },
                        "on_thursday": {
                            "type": "boolean",
                            "description": "Default False. Whether the schedule is active on Thursday.",
                        },
                        "on_friday": {
                            "type": "boolean",
                            "description": "Default False. Whether the schedule is active on Friday.",
                        },
                        "on_saturday": {
                            "type": "boolean",
                            "description": "Default False. Whether the schedule is active on Saturday.",
                        },
                        "on_sunday": {
                            "type": "boolean",
                            "description": "Default False. Whether the schedule is active on Sunday.",
                        },
                        "time": {
                            "type": "string",
                            "description": "The time when the automation should trigger. Format: HH:MM:SS (24-hour format, e.g. '14:30:00').",
                        },
                    },
                    "required": [
                        "automation_id",
                        "time",
                    ],
                },
            },
        }
