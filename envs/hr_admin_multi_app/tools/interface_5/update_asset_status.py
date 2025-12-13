import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class UpdateAssetStatus(Tool):
    """Update the status of an employee asset."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        asset_id: str,
        new_status: str,
        note: Optional[str] = None,
    ) -> str:
        """
        Update asset status and optionally attach a note.

        Allowed statuses: returned, missing, damaged, assigned.
        """

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data container"})

        assets = data.get("employee_assets")
        if not isinstance(assets, dict):
            return json.dumps({"success": False, "error": "employee_assets store missing"})

        if not isinstance(asset_id, str) or not asset_id.strip():
            return json.dumps({"success": False, "error": "asset_id must be provided"})
        record = assets.get(asset_id)
        if not record:
            return json.dumps({"success": False, "error": f"Asset '{asset_id}' not found"})

        if not isinstance(new_status, str) or not new_status.strip():
            return json.dumps({"success": False, "error": "new_status must be provided"})
        normalized_status = new_status.strip().lower()
        allowed_statuses = {"returned", "missing", "damaged", "assigned"}
        if normalized_status not in allowed_statuses:
            return json.dumps({"success": False, "error": f"new_status must be one of {', '.join(sorted(allowed_statuses))}"})

        record["status"] = normalized_status
        if note is not None:
            record["note"] = note
        timestamp = "2025-11-16T23:59:00"
        record["last_updated"] = timestamp

        return json.dumps(
            {
                "success": True,
                "message": f"Asset {asset_id} status updated",
                "asset": record,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_asset_status",
                "description": "Update the status of an employee asset.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asset_id": {
                            "type": "string",
                            "description": "Identifier of the employee asset being updated.",
                        },
                        "new_status": {
                            "type": "string",
                            "description": "New asset status; allowed values: returned, missing, damaged, assigned.",
                        },
                        "note": {
                            "type": "string",
                            "description": "Optional note explaining the status change.",
                        },
                    },
                    "required": ["asset_id", "new_status"],
                },
            },
        }
