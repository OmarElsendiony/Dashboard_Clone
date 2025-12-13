import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetDepartment(Tool):
    """
    Retrieve or search for departments with flexible filters.
    - Returns ALL departments when no filters are provided.
    - Applies all provided filters using AND logic.
    - Safe handling of ID comparisons (cast to str), enums, and datetime prefix matches.
    - Case-insensitive partial matching for name.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        department_id: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[str] = None,
        head_of_department_id: Optional[str] = None,
        created_at: Optional[str] = None,
        last_updated: Optional[str] = None,
    ) -> str:
        """
        Return a JSON string:
          {"success": True, "departments": [...]} on success
          {"success": False, "error": "..."} on error
        """

        # --- Basic input validation ---
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        departments_dict = data.get("departments", {})
        if not isinstance(departments_dict, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid departments container: expected dict at data['departments']",
                }
            )

        # --- Validate enum values if provided ---
        valid_statuses = ["active", "inactive"]

        if status is not None and status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status value: '{status}'. Must be one of {valid_statuses}",
                }
            )

        # --- Collect active filters (keep None out) ---
        filters = {
            "department_id": department_id,
            "name": name,
            "status": status,
            "head_of_department_id": head_of_department_id,
            "created_at": created_at,
            "last_updated": last_updated,
        }
        active_filters = {k: v for k, v in filters.items() if v is not None}

        # Start with all departments (dict copy to avoid mutating original rows)
        all_departments = [
            d.copy() for d in departments_dict.values() if isinstance(d, dict)
        ]

        # If no filters, return everything
        if not active_filters:
            return json.dumps({"success": True, "departments": all_departments})

        # --- Apply filters incrementally (AND logic) ---
        results = all_departments

        # ID / FK filters (compare as string)
        if department_id is not None:
            did = str(department_id)
            results = [d for d in results if d.get("department_id") == did]

        if head_of_department_id is not None:
            hid = str(head_of_department_id)
            results = [d for d in results if d.get("head_of_department_id") == hid]

        # Exact string filters
        if status is not None:
            results = [d for d in results if d.get("status") == status]

        # Case-insensitive partial matches
        if name is not None:
            try:
                pat = re.compile(re.escape(name), re.IGNORECASE)
                results = [
                    d
                    for d in results
                    if "name" in d and d["name"] and pat.search(d["name"])
                ]
            except re.error:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid regex pattern in name: {name}",
                    }
                )

        # Datetime prefix filters (e.g., "2024-01-05")
        if created_at is not None:
            results = [
                d for d in results if d.get("created_at", "").startswith(created_at)
            ]

        if last_updated is not None:
            results = [
                d for d in results if d.get("last_updated", "").startswith(last_updated)
            ]

        return json.dumps({"success": True, "departments": results})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """
        Tool schema for function-calling.
        """
        return {
            "type": "function",
            "function": {
                "name": "get_department",
                "description": "Retrieves departments from the HR system based on search criteria. A department is an organizational unit within the company. When called with no parameters, returns all departments in the system. When called with parameters, filters and returns only matching departments. You can combine multiple filters to narrow down results. All filters support AND logic (all conditions must match).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "department_id": {
                            "type": "string",
                            "description": "The unique identifier for a specific department. Performs exact match. ",
                        },
                        "name": {
                            "type": "string",
                            "description": "Searches within department names. Performs partial, case-insensitive matching. ",
                        },
                        "status": {
                            "type": "string",
                            "description": "Filters by department status. The accepted values are 'active' and 'inactive'. 'active' = currently operational departments. 'inactive' = departments that have been deactivated. Performs exact match.",
                        },
                        "head_of_department_id": {
                            "type": "string",
                            "description": "Filters departments by their head/manager's employee ID. Performs exact match. ",
                        },
                        "created_at": {
                            "type": "string",
                            "description": "Filters departments by creation date/time. Performs prefix matching on ISO datetime format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS). ",
                        },
                        "last_updated": {
                            "type": "string",
                            "description": "Filters departments by last update date/time. Performs prefix matching on ISO datetime format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS). ",
                        },
                    },
                    "required": [],
                },
            },
        }

