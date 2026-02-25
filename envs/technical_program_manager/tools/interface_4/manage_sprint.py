import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class ManageSprint(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        sprint_id: Optional[str] = None,
        project_id: Optional[str] = None,
        sprint_name: Optional[str] = None,
        state: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-11T23:59:00"

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        action_str = str(action).strip().lower()
        valid_actions = ["create", "update", "delete"]
        if action_str not in valid_actions:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid action '{action_str}'. Valid values: {', '.join(valid_actions)}",
                }
            )

        sprints = data.get("sprints", {})
        projects = data.get("projects", {})
        work_items = data.get("work_items", {})
        valid_states = ["future", "active", "completed", "closed"]

        if action_str == "create":
            if sprint_id is not None:
                return json.dumps(
                    {
                        "success": False,
                        "error": "sprint_id should not be provided when creating a sprint",
                    }
                )

            if not all([project_id, sprint_name, start_date, end_date]):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Create requires: project_id, sprint_name, start_date, end_date",
                    }
                )

            pid = str(project_id).strip()
            name_str = str(sprint_name).strip()
            start_str = str(start_date).strip()
            end_str = str(end_date).strip()

            if not name_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Sprint name cannot be empty or whitespace",
                    }
                )

            if pid not in projects:
                return json.dumps({"success": False, "error": f"Project '{pid}' not found"})

            project_status = str(projects[pid].get("status", ""))
            if project_status not in ["open", "in_progress"]:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Project '{pid}' status is '{project_status}'. Must be 'open' or 'in_progress'.",
                    }
                )

            state_str = str(state).strip() if state else "future"
            if state and state_str not in valid_states:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid state '{state_str}'. Valid values: {', '.join(valid_states)}",
                    }
                )

            # Duplicate sprint name check within project
            for s in sprints.values():
                if str(s.get("project_id", "")) == pid and str(s.get("sprint_name", "")).lower() == name_str.lower():
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Sprint with name '{name_str}' already exists in project '{pid}'",
                        }
                    )

            if end_str <= start_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": "End date must be after start date",
                    }
                )

            if sprints:
                max_id = max(int(k) for k in sprints.keys())
                new_id = str(max_id + 1)
            else:
                new_id = "1"

            new_sprint = {
                "sprint_id": new_id,
                "project_id": pid,
                "sprint_name": name_str,
                "state": state_str,
                "start_date": start_str,
                "end_date": end_str,
                "created_at": timestamp,
                "updated_at": timestamp,
            }

            sprints[new_id] = new_sprint

            response = {
                "sprint_id": str(new_sprint.get("sprint_id", "")),
                "project_id": str(new_sprint.get("project_id", "")),
                "sprint_name": str(new_sprint.get("sprint_name", "")),
                "state": str(new_sprint.get("state", "")),
                "start_date": str(new_sprint.get("start_date", "")) if new_sprint.get("start_date") else None,
                "end_date": str(new_sprint.get("end_date", "")) if new_sprint.get("end_date") else None,
                "created_at": str(new_sprint.get("created_at", "")),
                "updated_at": str(new_sprint.get("updated_at", "")),
            }
            return json.dumps({"success": True, "sprint": response})

        elif action_str == "update":
            if not sprint_id:
                return json.dumps(
                    {"success": False, "error": "Update requires: sprint_id"}
                )

            sid = str(sprint_id).strip()
            sprint = sprints.get(sid)
            if sprint is None:
                return json.dumps(
                    {"success": False, "error": f"Sprint '{sid}' not found"}
                )

            if not any([sprint_name, state, start_date, end_date]):
                return json.dumps(
                    {
                        "success": False,
                        "error": "At least one field to update must be provided",
                    }
                )

            current_state = str(sprint.get("state", ""))

            # Strict SOP guard: only future/active sprints can be updated (SOP line 166)
            if current_state in ["completed", "closed"]:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Cannot update sprint with state '{current_state}'. Sprint must be 'future' or 'active'.",
                    }
                )

            if sprint_name is not None:
                name_val = str(sprint_name).strip()
                if not name_val:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Sprint name cannot be empty or whitespace",
                        }
                    )
                sprint_pid = str(sprint.get("project_id", ""))
                for s in sprints.values():
                    if (str(s.get("sprint_id", "")) != sid
                            and str(s.get("project_id", "")) == sprint_pid
                            and str(s.get("sprint_name", "")).lower() == name_val.lower()):
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"Sprint with name '{name_val}' already exists in project '{sprint_pid}'",
                            }
                        )
                sprint["sprint_name"] = name_val

            if state is not None:
                state_val = str(state).strip()
                if state_val not in valid_states:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid state '{state_val}'. Valid values: {', '.join(valid_states)}",
                        }
                    )
                # Enforce state transition rules (SOP: future→active, active→completed)
                valid_transitions = {
                    "future": ["active"],
                    "active": ["completed"],
                }
                allowed = valid_transitions.get(current_state, [])
                if state_val not in allowed:
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Invalid state transition from '{current_state}' to '{state_val}'. Allowed transitions: {', '.join(allowed) if allowed else 'none'}",
                        }
                    )
                sprint["state"] = state_val

            # Date ordering validation (only when a date is being changed)
            if start_date is not None or end_date is not None:
                effective_start = str(start_date).strip() if start_date is not None else str(sprint.get("start_date", ""))
                effective_end = str(end_date).strip() if end_date is not None else str(sprint.get("end_date", ""))
                if effective_start and effective_end and effective_end <= effective_start:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "End date must be after start date",
                        }
                    )
                if start_date is not None:
                    sprint["start_date"] = effective_start
                if end_date is not None:
                    sprint["end_date"] = effective_end

            sprint["updated_at"] = timestamp

            response = {
                "sprint_id": str(sprint.get("sprint_id", "")),
                "project_id": str(sprint.get("project_id", "")),
                "sprint_name": str(sprint.get("sprint_name", "")),
                "state": str(sprint.get("state", "")),
                "start_date": str(sprint.get("start_date", "")) if sprint.get("start_date") else None,
                "end_date": str(sprint.get("end_date", "")) if sprint.get("end_date") else None,
                "created_at": str(sprint.get("created_at", "")),
                "updated_at": str(sprint.get("updated_at", "")),
            }
            return json.dumps({"success": True, "sprint": response})

        elif action_str == "delete":
            if not sprint_id:
                return json.dumps(
                    {"success": False, "error": "Delete requires: sprint_id"}
                )

            sid = str(sprint_id).strip()
            if sid not in sprints:
                return json.dumps(
                    {"success": False, "error": f"Sprint '{sid}' not found"}
                )

            sprint = sprints[sid]

            # State must be "future" to delete
            sprint_state = str(sprint.get("state", ""))
            if sprint_state != "future":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Cannot delete sprint with state '{sprint_state}'. Only sprints with state 'future' can be deleted.",
                    }
                )

            # No work items with open statuses assigned
            for wi in work_items.values():
                if wi.get("sprint_id") is not None and str(wi.get("sprint_id", "")) == sid:
                    wi_status = str(wi.get("status", ""))
                    if wi_status in ["open", "in_progress", "blocked"]:
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"Cannot delete: sprint has issues with open statuses",
                            }
                        )

            deleted_sprint = sprints.pop(sid)

            # Cascade cleanup: unlink work items from deleted sprint
            for wi in work_items.values():
                if wi.get("sprint_id") is not None and str(wi.get("sprint_id", "")) == sid:
                    wi["sprint_id"] = None

            return json.dumps(
                {
                    "success": True,
                    "message": f"Sprint '{str(deleted_sprint.get('sprint_name', ''))}' has been deleted",
                }
            )

        return json.dumps({"success": False, "error": "Unexpected error"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "manage_sprint",
                "description": "Manages sprint lifecycle by creating, updating, or deleting sprint records.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "The action to perform",
                            "enum": ["create", "update", "delete"],
                        },
                        "sprint_id": {
                            "type": "string",
                            "description": "Unique sprint identifier.",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Unique project identifier.",
                        },
                        "sprint_name": {
                            "type": "string",
                            "description": "Sprint name",
                        },
                        "state": {
                            "type": "string",
                            "description": "Sprint state. Default for new sprints is 'future'.",
                            "enum": ["future", "active", "completed", "closed"],
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Sprint start date timestamp",
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Sprint end date timestamp",
                        },
                    },
                    "required": ["action"],
                    "allOf": [
                        {
                            "if": {
                                "properties": {"action": {"enum": ["create"]}}
                            },
                            "then": {
                                "required": ["project_id", "sprint_name", "start_date", "end_date"]
                            },
                        },
                        {
                            "if": {
                                "properties": {"action": {"enum": ["update"]}}
                            },
                            "then": {
                                "required": ["sprint_id"],
                                "anyOf": [
                                    {"required": ["sprint_name"]},
                                    {"required": ["state"]},
                                    {"required": ["start_date"]},
                                    {"required": ["end_date"]},
                                ],
                            },
                        },
                        {
                            "if": {
                                "properties": {"action": {"enum": ["delete"]}}
                            },
                            "then": {
                                "required": ["sprint_id"]
                            },
                        },
                    ],
                },
            },
        }
