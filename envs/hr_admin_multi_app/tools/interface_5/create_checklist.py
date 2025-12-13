import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class CreateChecklist(Tool):
    """Create a new onboarding or offboarding checklist for an employee."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        emp_id: str,
        status: Optional[str] = "pending",
        checklist_type: str = "",
    ) -> str:
        """
        Create a checklist tied to the employee.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(key) for key in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        employees = data.get("employees")
        checklists = data.get("checklists")
        if not isinstance(employees, dict) or not isinstance(checklists, dict):
            return json.dumps({"success": False, "error": "Missing employees or checklists store"})

        if not isinstance(emp_id, str) or not emp_id.strip():
            return json.dumps({"success": False, "error": "emp_id must be provided"})

        employee = employees.get(emp_id)
        if not employee:
            return json.dumps({"success": False, "error": f"Employee '{emp_id}' not found"})

        for record in checklists.values():
            if record.get("employee_id") == emp_id:
                return json.dumps({"success": False, "error": f"Checklist already exists for employee '{emp_id}'"})

        status_value = status.strip().lower() if isinstance(status, str) else "pending"
        if status_value not in {"pending", "completed"}:
            return json.dumps({"success": False, "error": "status must be pending or completed"})

        employee_status = str(employee.get("status", "")).strip().lower()
        if employee_status not in {"active", "inactive"}:
            return json.dumps({"success": False, "error": "Checklist creation allowed only for active or inactive employees"})

        allowed_types = {"onboarding", "offboarding"}
        normalized_type = checklist_type.strip().lower() if isinstance(checklist_type, str) and checklist_type.strip() else ""
        if normalized_type not in allowed_types:
            return json.dumps({"success": False, "error": "checklist_type must be onboarding or offboarding"})

        if normalized_type == "onboarding" and employee_status != "active":
            return json.dumps({"success": False, "error": "Onboarding checklists require an active employee"})
        if normalized_type == "offboarding" and employee_status != "inactive":
            return json.dumps({"success": False, "error": "Offboarding checklists require an inactive employee"})

        timestamp = "2025-12-12T12:00:00"
        checklist_id = generate_id(checklists)
        record = {
            "checklist_id": checklist_id,
            "checklist_type": normalized_type,
            "employee_id": emp_id,
            "status": status_value,
            "created_at": timestamp,
            "last_updated": timestamp,
        }
        checklists[checklist_id] = record

        return json.dumps(
            {
                "success": True,
                "message": f"{normalized_type.title()} checklist created for employee {emp_id}",
                "checklist": record,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_checklist",
                "description": (
                    "Create an onboarding or offboarding checklist for an employee."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "emp_id": {
                            "type": "string",
                            "description": "Employee identifier that will own the checklist.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Checklist status; allowed values are pending or completed. Defaults to pending.",
                        },
                        "checklist_type": {
                            "type": "string",
                            "description": "Checklist type; must be onboarding or offboarding.",
                        },
                    },
                    "required": ["emp_id", "checklist_type"],
                },
            },
        }
