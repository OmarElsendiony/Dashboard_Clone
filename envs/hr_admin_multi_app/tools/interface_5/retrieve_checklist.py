import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class RetrieveChecklist(Tool):
    """Fetch onboarding/offboarding checklists filtered by employee, type, or status."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        status: Optional[str] = None,
        checklist_type: Optional[str] = None,
    ) -> str:
        """
        Fetch checklists for an employee. Optional filters: status (pending/completed) and checklist_type (onboarding/offboarding).
        """

        def normalize(value: Optional[str]) -> Optional[str]:
            return value.strip().lower() if isinstance(value, str) and value.strip() else None

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        checklists = data.get("checklists")
        employees = data.get("employees")
        if not isinstance(checklists, dict) or not isinstance(employees, dict):
            return json.dumps({"success": False, "error": "Missing employees or checklists store"})

        if not employee_id or employee_id not in employees:
            return json.dumps({"success": False, "error": f"Employee '{employee_id}' not found"})

        status_filter = normalize(status)
        if status_filter and status_filter not in {"pending", "completed"}:
            return json.dumps({"success": False, "error": "status must be pending or completed"})

        type_filter = normalize(checklist_type)
        if type_filter and type_filter not in {"onboarding", "offboarding"}:
            return json.dumps({"success": False, "error": "checklist_type must be onboarding or offboarding"})

        results = []
        for checklist_id, checklist in checklists.items():
            if not isinstance(checklist, dict):
                continue
            if checklist.get("employee_id") != employee_id:
                continue
            if status_filter and normalize(checklist.get("status")) != status_filter:
                continue
            if type_filter and normalize(checklist.get("checklist_type")) != type_filter:
                continue
            record = dict(checklist)
            record["checklist_id"] = checklist_id
            results.append(record)

        if not results:
            return json.dumps({"success": False, "error": "No checklists found for provided criteria"})

        return json.dumps({"success": True, "count": len(results), "checklists": results})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "retrieve_checklist",
                "description": "Retrieve onboarding/offboarding checklists for an employee with optional status/type filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Employee identifier whose checklists are requested.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional status filter; allowed values: pending, completed.",
                        },
                        "checklist_type": {
                            "type": "string",
                            "description": "Optional checklist type filter; allowed values: onboarding, offboarding.",
                        },
                    },
                    "required": ["employee_id"],
                },
            },
        }
