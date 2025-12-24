import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class GetAutomation(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        automation_id: str,
    ) -> str:
        """
        Retrieve automation details including triggers and actions.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        routines = data.get("routines")
        routine_triggers = data.get("routine_triggers")
        routine_actions = data.get("routine_actions")

        if not isinstance(homes, dict):
            return json.dumps({"success": False, "error": "homes store missing"})
        if not isinstance(routines, dict):
            return json.dumps({"success": False, "error": "routines store missing"})

        if not isinstance(home_name, str) or not home_name.strip():
            return json.dumps({"success": False, "error": "home_name must be provided"})
        home_name = home_name.strip()

        # Find home by name
        home_id = None
        for hid, home in homes.items():
            if home.get("home_name", "").strip().lower() == home_name.lower():
                home_id = hid
                break
        if not home_id:
            return json.dumps({"success": False, "error": f"Home '{home_name}' not found"})

        if not isinstance(automation_id, str) or not automation_id.strip():
            return json.dumps({"success": False, "error": "automation_id must be provided"})
        automation_id = automation_id.strip()

        if automation_id not in routines:
            return json.dumps({"success": False, "error": f"Automation '{automation_id}' not found"})

        routine = dict(routines[automation_id])
        if routine.get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Automation '{automation_id}' does not belong to home '{home_name}'"})

        triggers = []
        if isinstance(routine_triggers, dict):
            for trigger in routine_triggers.values():
                if trigger.get("routine_id") == automation_id:
                    triggers.append(trigger)

        actions = []
        if isinstance(routine_actions, dict):
            for action in routine_actions.values():
                if action.get("routine_id") == automation_id:
                    actions.append(action)

        presented_triggers = []
        for t in triggers:
            presented_triggers.append({
                "trigger_id": t.get("trigger_id"),
                "automation_id": t.get("routine_id"),
                "trigger_type": t.get("trigger_type"),
                "schedule_id": t.get("routine_schedule_id"),
                "solar_event": t.get("solar_event"),
                "accessory_id": t.get("device_id"),
                "created_at": t.get("created_at"),
                "updated_at": t.get("updated_at"),
            })

        presented_actions = []
        for a in actions:
            presented_actions.append({
                "action_id": a.get("action_id"),
                "automation_id": a.get("routine_id"),
                "action_type": a.get("action_type"),
                "accessory_id": a.get("target_device_id"),
                "scene_id": a.get("target_scene_id"),
                "notification_id": a.get("target_notification_id"),
                "created_at": a.get("created_at"),
                "updated_at": a.get("updated_at"),
            })

        presented = {
            "automation_id": routine.get("routine_id"),
            "automation_name": routine.get("routine_name"),
            "status": routine.get("status"),
            "description": routine.get("description"),
            "created_at": routine.get("created_at"),
            "updated_at": routine.get("updated_at"),
            "triggers": presented_triggers,
            "actions": presented_actions,
        }

        return json.dumps({"success": True, "automation": presented})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_automation",
                "description": "Get detailed information about a specific automation routine including triggers and actions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "automation_id": {
                            "type": "string",
                            "description": "Identifier of the automation.",
                        },
                    },
                    "required": ["home_name", "automation_id"],
                },
            },
        }

