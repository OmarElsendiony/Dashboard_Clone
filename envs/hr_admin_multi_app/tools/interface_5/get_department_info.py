import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class GetDepartmentInfo(Tool):
    """Fetch department details by name with optional status filtering."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        department_name: Optional[str] = None,
        status: Optional[str] = None,
        department_id: Optional[str] = None,
    ) -> str:
        """
        Return a department record that matches the provided department_name and optional status filter.
        """

        def normalize(value: Optional[str]) -> Optional[str]:
            return value.strip().lower() if isinstance(value, str) and value.strip() else None

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        departments = data.get("departments")
        if not isinstance(departments, dict):
            return json.dumps({"success": False, "error": "Departments store missing"})

        if not department_name and not department_id:
            return json.dumps({"success": False, "error": "Provide department_name or department_id"})

        allowed_statuses = {"active", "inactive"}
        status_filter = None
        if status:
            status_filter = normalize(status)
            if status_filter not in allowed_statuses:
                return json.dumps({"success": False, "error": "status must be one of active or inactive"})

        target_record = None
        target_name = normalize(department_name) if isinstance(department_name, str) else None
        target_id = department_id.strip() if isinstance(department_id, str) and department_id.strip() else None

        if target_id:
            target_record = departments.get(target_id)
            if not target_record:
                return json.dumps({"success": False, "error": f"Department id '{target_id}' not found"})
            if target_name and normalize(target_record.get("name")) != target_name:
                return json.dumps({"success": False, "error": "department_id and department_name refer to different departments"})
        else:
            if not target_name:
                return json.dumps({"success": False, "error": "department_name must be provided when department_id is absent"})
            for record in departments.values():
                if normalize(record.get("name")) == target_name:
                    target_record = record
                    break

        if not target_record:
            reference = department_id if target_id else department_name
            return json.dumps({"success": False, "error": f"Department '{reference}' not found"})

        record_status = normalize(target_record.get("status"))
        if status_filter and record_status != status_filter:
            return json.dumps({"success": False, "error": "Department found but status mismatch"})

        payload = dict(target_record)
        payload["department_id"] = target_record.get("department_id")
        payload["status"] = target_record.get("status")
        return json.dumps({"success": True, "department": payload})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_department_info",
                "description": "Retrieve a department record by name, optionally filtering by status (active/inactive).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "department_name": {
                            "type": "string",
                            "description": "Exact name of the department to look up.",
                        },
                        "department_id": {
                            "type": "string",
                            "description": "Optional department identifier. Provide either department_name or department_id.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional status filter; allowed values: active, inactive.",
                        },
                    },
                    "required": [],
                },
            },
        }
