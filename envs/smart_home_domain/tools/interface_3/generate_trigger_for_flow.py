import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GenerateTriggerForFlow(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        flow_id: str,
        trigger_type: str,
        flow_schedule_id: Optional[str] = None,
        solar_event: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> str:
        """Create a trigger record for an automation flow."""
        try:
            if not isinstance(data, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Invalid payload: data must be the state dictionary.",
                    }
                )

            routines = data.get("routines")
            triggers = data.get("routine_triggers")
            schedules = data.get("routine_schedules", {})
            devices = data.get("devices", {})

            if not isinstance(routines, dict) or not isinstance(triggers, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Missing flows or flows_triggers collections in the dataset.",
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
                        "error": "Flow not found.",
                    }
                )

            if not isinstance(trigger_type, str) or not trigger_type.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "trigger_type is required.",
                    }
                )

            normalized_trigger_type = trigger_type.strip().lower()
            allowed_types = {"manual", "time_based", "solar_event", "device_state"}
            if normalized_trigger_type not in allowed_types:
                return json.dumps(
                    {
                        "success": False,
                        "error": "trigger_type must be one of manual, time_based, solar_event, or device_state.",
                    }
                )

            schedule_id_clean = None
            if normalized_trigger_type in {"time_based", "solar_event"}:
                if (
                    not isinstance(flow_schedule_id, str)
                    or not flow_schedule_id.strip()
                ):
                    return json.dumps(
                        {
                            "success": False,
                            "error": "flow_schedule_id is required for time_based and solar_event triggers.",
                        }
                    )
                schedule_id_clean = flow_schedule_id.strip()
                if schedule_id_clean not in schedules:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "flow_schedule_id not found. Define the time schedule first.",
                        }
                    )

            solar_event_clean = None
            if normalized_trigger_type == "solar_event":
                if not isinstance(solar_event, str) or not solar_event.strip():
                    return json.dumps(
                        {
                            "success": False,
                            "error": "solar_event is required when trigger_type is solar_event.",
                        }
                    )
                solar_event_clean = solar_event.strip().lower()
                if solar_event_clean not in {"sunrise", "sunset"}:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "solar_event must be 'sunrise' or 'sunset'.",
                        }
                    )

            device_id_clean = None
            if normalized_trigger_type == "device_state":
                if not isinstance(device_id, str) or not device_id.strip():
                    return json.dumps(
                        {
                            "success": False,
                            "error": "device_id is required when trigger_type is device_state.",
                        }
                    )
                device_id_clean = device_id.strip()
                if device_id_clean not in devices:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "device_id not found in the device registry.",
                        }
                    )
                device = devices[device_id_clean]
                device_type = str(device.get("device_type", ""))
                if not device_type.endswith("sensor"):
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Device '{device_id_clean}' has device_type '{device_type}' which is not a sensor. Only sensor devices can be used for device_state triggers.",
                        }
                    )

            numeric_ids = []
            for key in triggers.keys():
                try:
                    numeric_ids.append(int(str(key)))
                except ValueError:
                    continue
            next_id = max(numeric_ids) + 1 if numeric_ids else len(triggers) + 1
            trigger_id = str(next_id)

            timestamp = "2025-12-19T23:59:00"
            new_trigger = {
                "trigger_id": trigger_id,
                "routine_id": flow_id_clean,
                "trigger_type": normalized_trigger_type,
                "routine_schedule_id": schedule_id_clean,
                "solar_event": solar_event_clean,
                "device_id": device_id_clean,
                "created_at": timestamp,
                "updated_at": timestamp,
            }
            triggers[trigger_id] = new_trigger

            return json.dumps(
                {
                    "success": True,
                    "message": f"Trigger '{trigger_id}' created for flow '{flow_id_clean}'.",
                    "trigger": {
                        "trigger_id": new_trigger["trigger_id"],
                        "flow_id": new_trigger["flow_id"],
                        "trigger_type": new_trigger["trigger_type"],
                        "flow_schedule_id": new_trigger["flow_schedule_id"],
                        "solar_event": new_trigger["solar_event"],
                        "device_id": new_trigger["device_id"],
                        "created_at": new_trigger["created_at"],
                        "updated_at": new_trigger["updated_at"],
                    },
                }
            )
        except Exception as exc:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Failed to generate trigger: {exc}",
                }
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "generate_trigger_for_flow",
                "description": (
                    "Create a trigger for an automation flow. "
                    "Supports manual, time_based (requires flow_schedule_id), solar_event (requires solar_event sunrise/sunset and flow_schedule_id), "
                    "and device_state (requires device_id) triggers."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "flow_id": {
                            "type": "string",
                            "description": "Required identifier of the target flow.",
                        },
                        "trigger_type": {
                            "type": "string",
                            "description": "Required trigger classification: manual, time_based, solar_event, or device_state.",
                        },
                        "flow_schedule_id": {
                            "type": "string",
                            "description": "Required when trigger_type is time_based or solar_event. References define_time_schedule output.",
                        },
                        "solar_event": {
                            "type": "string",
                            "description": "Required when trigger_type is solar_event. Accepts sunrise or sunset.",
                        },
                        "device_id": {
                            "type": "string",
                            "description": "Required when trigger_type is device_state. Provide the device identifier from discover_household_devices.",
                        },
                    },
                    "required": ["flow_id", "trigger_type"],
                },
            },
        }
