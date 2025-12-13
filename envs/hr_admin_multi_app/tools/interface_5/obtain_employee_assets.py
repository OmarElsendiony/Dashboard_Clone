import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class ObtainEmployeeAssets(Tool):
    """Return all assets linked to a specific employee."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        emp_id: str,
        item_name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Fetch employee assets by employee id with optional item name and status filters.
        """

        def normalize(value: Optional[str]) -> Optional[str]:
            return value.strip().lower() if isinstance(value, str) and value.strip() else None

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        employee_assets = data.get("employee_assets")
        employees = data.get("employees")
        if not isinstance(employee_assets, dict) or not isinstance(employees, dict):
            return json.dumps({"success": False, "error": "Missing employees or employee_assets store"})

        if not isinstance(emp_id, str) or not emp_id.strip():
            return json.dumps({"success": False, "error": "emp_id must be provided"})

        if emp_id not in employees:
            return json.dumps({"success": False, "error": f"Employee '{emp_id}' not found"})

        status_filter = normalize(status)
        if status_filter and status_filter not in {"returned", "missing", "damaged", "assigned"}:
            return json.dumps({"success": False, "error": "status must be one of returned, missing, damaged, assigned"})

        name_filter = normalize(item_name)

        results = []
        for asset_id, asset in employee_assets.items():
            if asset.get("employee_id") != emp_id:
                continue
            if status_filter and normalize(asset.get("status")) != status_filter:
                continue
            if name_filter:
                asset_name = (asset.get("item_name") or "").lower()
                if name_filter not in asset_name:
                    continue
            results.append({"asset_id": asset_id, **asset})

        if not results:
            return json.dumps({"success": False, "error": f"No assets found for employee '{emp_id}'"})

        return json.dumps(
            {
                "success": True,
                "count": len(results),
                "assets": results,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "obtain_employee_assets",
                "description": "Get employee assets optionally filtered by item name and asset status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "emp_id": {
                            "type": "string",
                            "description": "Employee identifier whose assets are requested.",
                        },
                        "item_name": {
                            "type": "string",
                            "description": "Optional substring filter applied to asset item names.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional status filter; allowed values: returned, missing, damaged, assigned.",
                        },
                    },
                    "required": ["emp_id"],
                },
            },
        }
