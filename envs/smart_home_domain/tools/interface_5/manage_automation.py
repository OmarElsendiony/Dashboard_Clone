import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ManageAutomation(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_name: str,
        action: str,
        automation_id: Optional[str] = None,
        automation_name: Optional[str] = None,
        new_automation_name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Update or delete an automation.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        homes = data.get("homes")
        routines = data.get("routines")
        routine_triggers = data.get("routine_triggers")
        routine_schedule = data.get("routine_schedules")
        routine_trigger_attributes = data.get("routine_trigger_attributes")
        routine_actions = data.get("routine_actions")
        routine_action_attributes = data.get("routine_action_attributes")

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

        # Exactly one of automation_id or automation_name must be provided
        if (automation_id is None and automation_name is None) or (automation_id is not None and automation_name is not None):
            return json.dumps({"success": False, "error": "Provide exactly one of automation_id or automation_name"})

        resolved_automation_id = None
        if automation_id is not None:
            if not isinstance(automation_id, str) or not automation_id.strip():
                return json.dumps({"success": False, "error": "automation_id must be a non-empty string"})
            resolved_automation_id = automation_id.strip()
            if resolved_automation_id not in routines:
                return json.dumps({"success": False, "error": f"Automation '{resolved_automation_id}' not found"})
        else:
            if not isinstance(automation_name, str) or not automation_name.strip():
                return json.dumps({"success": False, "error": "automation_name must be a non-empty string"})
            name_val = automation_name.strip().lower()
            matches = []
            for rid, r in routines.items():
                if r.get("home_id") == home_id and r.get("routine_name", "").strip().lower() == name_val:
                    matches.append(rid)
            if not matches:
                return json.dumps({"success": False, "error": f"Automation '{automation_name.strip()}' not found"})
            if len(matches) > 1:
                return json.dumps({"success": False, "error": f"Multiple automations named '{automation_name.strip()}' found in home '{home_name}'"})
            resolved_automation_id = matches[0]

        routine = routines[resolved_automation_id]
        if routine.get("home_id") != home_id:
            return json.dumps({"success": False, "error": f"Automation '{resolved_automation_id}' does not belong to home '{home_name}'"})

        if not isinstance(action, str) or not action.strip():
            return json.dumps({"success": False, "error": "action must be provided"})
        action_val = action.strip().lower()
        if action_val not in {"update", "delete"}:
            return json.dumps({"success": False, "error": "action must be one of update, delete"})

        if action_val == "delete":
            # Cascade delete triggers + trigger attributes + schedule + actions + action attributes
            trigger_ids = []
            if isinstance(routine_triggers, dict):
                trigger_ids = [tid for tid, t in routine_triggers.items() if t.get("routine_id") == resolved_automation_id]
                for tid in trigger_ids:
                    routine_triggers.pop(tid, None)

            if isinstance(routine_trigger_attributes, dict) and trigger_ids:
                to_delete = [aid for aid, a in routine_trigger_attributes.items() if a.get("trigger_id") in trigger_ids]
                for aid in to_delete:
                    routine_trigger_attributes.pop(aid, None)

            if isinstance(routine_schedule, dict):
                sched_ids = [sid for sid, s in routine_schedule.items() if s.get("routine_id") == resolved_automation_id]
                for sid in sched_ids:
                    routine_schedule.pop(sid, None)

            action_ids = []
            if isinstance(routine_actions, dict):
                action_ids = [aid for aid, a in routine_actions.items() if a.get("routine_id") == resolved_automation_id]
                for aid in action_ids:
                    routine_actions.pop(aid, None)

            if isinstance(routine_action_attributes, dict) and action_ids:
                to_delete = [aid for aid, a in routine_action_attributes.items() if a.get("action_id") in action_ids]
                for aid in to_delete:
                    routine_action_attributes.pop(aid, None)

            deleted = routines.pop(resolved_automation_id)
            return json.dumps({
                "success": True,
                "deleted_automation": {
                    "automation_id": deleted.get("routine_id"),
                    "automation_name": deleted.get("routine_name"),
                    "status": deleted.get("status"),
                    "description": deleted.get("description"),
                    "created_at": deleted.get("created_at"),
                    "updated_at": deleted.get("updated_at"),
                },
            })

        updates = False

        if new_automation_name is not None:
            if not isinstance(new_automation_name, str) or not new_automation_name.strip():
                return json.dumps({"success": False, "error": "new_automation_name must be a non-empty string"})
            new_name = new_automation_name.strip()
            
            for rid, r in routines.items():
                if rid != resolved_automation_id and r.get("home_id") == home_id and r.get("routine_name", "").strip().lower() == new_name.lower():
                    return json.dumps({"success": False, "error": f"Automation '{new_name}' already exists in this home"})
            
            routine["routine_name"] = new_name
            updates = True

        if description is not None:
            routine["description"] = description.strip() if isinstance(description, str) and description.strip() else None
            updates = True

        if status is not None:
            if not isinstance(status, str):
                return json.dumps({"success": False, "error": "status must be a string"})
            status_val = status.strip().lower()
            if status_val not in {"enabled", "disabled"}:
                return json.dumps({"success": False, "error": "status must be one of enabled, disabled"})
            routine["status"] = status_val
            updates = True

        if not updates:
            return json.dumps({"success": False, "error": "No updates provided"})

        routine["updated_at"] = "2025-12-19T23:59:00"

        return json.dumps({
            "success": True,
            "automation": {
                "automation_id": routine.get("routine_id"),
                "automation_name": routine.get("routine_name"),
                "status": routine.get("status"),
                "description": routine.get("description"),
                "created_at": routine.get("created_at"),
                "updated_at": routine.get("updated_at"),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "manage_automation",
                "description": "Update automation routine details.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_name": {
                            "type": "string",
                            "description": "Name of the home.",
                        },
                        "automation_id": {
                            "type": "string",
                            "description": "Identifier of the automation (provide either automation_id or automation_name).",
                        },
                        "automation_name": {
                            "type": "string",
                            "description": "Name of the automation (provide either automation_id or automation_name).",
                        },
                        "action": {
                            "type": "string",
                            "description": "Action to perform; allowed values: update, delete.",
                        },
                        "new_automation_name": {
                            "type": "string",
                            "description": "Optional new name for the automation (update action only).",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional new description.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional new status; allowed values: enabled, disabled.",
                        },
                    },
                    "required": ["home_name", "action"],
                },
            },
        }

