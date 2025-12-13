import json
from typing import Any, Dict, List, Optional

from tau_bench.envs.tool import Tool


class RetrieveChecklistTask(Tool):
    """Fetch checklist tasks using checklist or employee identifiers."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        checklist_id: Optional[str] = None,
        employee_id: Optional[str] = None,
        status: Optional[str] = None,
        name: Optional[str] = None,
    ) -> str:
        """
        Retrieve checklist tasks linked to a specific checklist or employee.

        At least one of checklist_id or employee_id must be provided. When both are supplied,
        the checklist must belong to the provided employee.
        """

        def normalize(value: Optional[str]) -> Optional[str]:
            return value.strip() if isinstance(value, str) and value.strip() else None

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        checklists = data.get("checklists")
        checklist_tasks = data.get("checklist_tasks")
        if not isinstance(checklists, dict) or not isinstance(checklist_tasks, dict):
            return json.dumps({"success": False, "error": "Missing checklists or checklist_tasks store"})

        checklist_id = normalize(checklist_id)
        employee_id = normalize(employee_id)
        name_filter = name.strip().lower() if isinstance(name, str) and name.strip() else None
        if not checklist_id and not employee_id:
            return json.dumps({"success": False, "error": "Provide checklist_id or employee_id"})

        allowed_statuses = {"pending", "completed"}
        status_filter = None
        if status:
            status_filter = normalize(status)
            if status_filter:
                status_filter = status_filter.lower()
            if status_filter not in allowed_statuses:
                return json.dumps({"success": False, "error": "status must be pending or completed"})

        target_checklists: List[Dict[str, Any]] = []

        if checklist_id:
            checklist = checklists.get(checklist_id)
            if not checklist:
                return json.dumps({"success": False, "error": f"Checklist '{checklist_id}' not found"})
            if employee_id and normalize(checklist.get("employee_id")) != employee_id:
                return json.dumps({"success": False, "error": "Checklist does not belong to provided employee"})
            target_checklists.append({"checklist_id": checklist_id, **checklist})
        else:
            for cl_id, record in checklists.items():
                if normalize(record.get("employee_id")) == employee_id:
                    target_checklists.append({"checklist_id": cl_id, **record})
            if not target_checklists:
                return json.dumps({"success": False, "error": f"No checklists found for employee '{employee_id}'"})

        target_ids = {item["checklist_id"] for item in target_checklists}
        tasks: List[Dict[str, Any]] = []
        for task_id, task in checklist_tasks.items():
            if task.get("checklist_id") not in target_ids:
                continue
            task_status = normalize(task.get("status"))
            if task_status:
                task_status = task_status.lower()
            if status_filter and task_status != status_filter:
                continue
            if name_filter and name_filter not in (task.get("name") or "").lower():
                continue
            tasks.append({"task_id": task_id, **task})

        if not tasks:
            return json.dumps({"success": False, "error": "No checklist tasks found for supplied criteria"})

        return json.dumps(
            {
                "success": True,
                "count": len(tasks),
                "checklists": target_checklists,
                "tasks": tasks,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "retrieve_checklist_task",
                "description": "Retrieve checklist tasks by checklist identifier or employee identifier.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "checklist_id": {
                            "type": "string",
                            "description": "Checklist identifier to fetch its tasks.",
                        },
                        "employee_id": {
                            "type": "string",
                            "description": "Employee identifier; returns tasks for all checklists owned by that employee.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional task status filter; allowed values: pending, completed.",
                        },
                        "name": {
                            "type": "string",
                            "description": "Optional task name filter.",
                        },
                    },
                    "required": [],
                },
            },
        }
