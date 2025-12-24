import json
import re
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class DefineTimeSchedule(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        flow_id: str,
        onset_time: str,
        weekly_schedule: Dict[str, Any],
    ) -> str:
        """Attach a time-based weekly schedule to a automation flow."""
        try:
            if not isinstance(data, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Invalid payload: data must be the state dictionary.",
                    }
                )

            routines = data.get("routines")
            schedules = data.get("routine_schedules")

            if not isinstance(routines, dict) or not isinstance(schedules, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Missing flow or flow_schedules collections in the dataset.",
                    }
                )

            if not isinstance(flow_id, str) or not flow_id.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "flow_id is required so the flow can be identified.",
                    }
                )

            flow_id_clean = flow_id.strip()
            if flow_id_clean not in routines:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Flow not found. Provide a valid flow_id",
                    }
                )

            if not isinstance(onset_time, str) or not onset_time.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "onset_time is required in HH:MM:SS format.",
                    }
                )

            normalized_time = onset_time.strip()
            if not re.fullmatch(r"\d{2}:\d{2}:\d{2}", normalized_time):
                return json.dumps(
                    {
                        "success": False,
                        "error": "onset_time must follow HH:MM:SS (24-hour clock).",
                    }
                )

            if not isinstance(weekly_schedule, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "weekly_schedule must be an object specifying which days the flow should run.",
                    }
                )

            days = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
            schedule_flags = {}
            active_count = 0
            for day in days:
                flag = bool(weekly_schedule.get(day, False))
                schedule_flags[f"on_{day}"] = flag
                if flag:
                    active_count += 1

            if active_count == 0:
                return json.dumps(
                    {
                        "success": False,
                        "error": "weekly_schedule must enable at least one day.",
                    }
                )

            numeric_ids = []
            for key in schedules.keys():
                try:
                    numeric_ids.append(int(str(key)))
                except ValueError:
                    continue
            next_id = max(numeric_ids) + 1 if numeric_ids else len(schedules) + 1
            schedule_id = str(next_id)

            new_schedule = {
                "schedule_id": schedule_id,
                "flow_id": flow_id_clean,
                "onset_time": normalized_time,
                **schedule_flags,
            }
            schedules[schedule_id] = new_schedule

            return json.dumps(
                {
                    "success": True,
                    "message": "Time schedule defined successfully.",
                    "schedule": {
                        "schedule_id": new_schedule["schedule_id"],
                        "flow_id": new_schedule["flow_id"],
                        "onset_time": new_schedule["onset_time"],
                        **schedule_flags,
                    },
                }
            )
        except Exception as exc:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Failed to define time schedule: {exc}",
                }
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "define_time_schedule",
                "description": (
                    "Attach a weekly time schedule to flow. "
                    "Requires flow_id, onset_time (HH:MM:SS), and a weekly_schedule object with boolean flags for monday-sunday. "
                    "At least one day must be enabled."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "flow_id": {
                            "type": "string",
                            "description": "Required identifier of the flow returned by create_flow_definition.",
                        },
                        "onset_time": {
                            "type": "string",
                            "description": "Required run time in HH:MM:SS (24-hour) format.",
                        },
                        "weekly_schedule": {
                            "type": "object",
                            "description": "Required mapping of weekday names to booleans (keys: monday, tuesday, wednesday, thursday, friday, saturday, sunday). To mark it false either do not add it in the input or add it with empty value ({'monday': ""}),",
                        },
                    },
                    "required": ["flow_id", "onset_time", "weekly_schedule"],
                },
            },
        }
