import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class RetrieveFlowInformation(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        flow_name: str,
        status: Optional[str] = None,
    ) -> str:
        """Retrieve automation flow  records for a household."""
        try:
            if not isinstance(data, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Invalid payload: data must be the state dictionary.",
                    }
                )

            routines = data.get("routines")
            if not isinstance(routines, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Missing flow collection in the dataset.",
                    }
                )

            if not isinstance(home_id, str) or not home_id.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "home_id is required so the household context is explicit.",
                    }
                )

            if not isinstance(flow_name, str) or not flow_name.strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": "flow_name is required.",
                    }
                )

            normalized_status = None
            if status is not None:
                if not isinstance(status, str) or not status.strip():
                    return json.dumps(
                        {
                            "success": False,
                            "error": "status must be 'enabled' or 'disabled' when provided.",
                        }
                    )
                normalized_status = status.strip().lower()
                if normalized_status not in {"enabled", "disabled"}:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "status must be 'enabled' or 'disabled' when provided.",
                        }
                    )

            home_id_clean = home_id.strip()
            flow_name_clean = flow_name.strip().lower()
            results = []
            for record in routines.values():
                if not isinstance(record, dict):
                    continue
                if str(record.get("home_id", "")).strip() != home_id_clean:
                    continue
                if str(record.get("routine_name", "")).strip().lower() != flow_name_clean:
                    continue
                if normalized_status and str(record.get("status", "")).strip().lower() != normalized_status:
                    continue
                results.append(
                    {
                        "flow_id": record.get("routine_id"),
                        "flow_name": record.get("routine_name"),
                        "status": record.get("status"),
                        "description": record.get("description"),
                        "home_id": record.get("home_id"),
                        "created_by_user_id": record.get("created_by_user_id"),
                        "created_at": record.get("created_at"),
                        "updated_at": record.get("updated_at"),
                    }
                )

            if not results:
                return json.dumps(
                    {
                        "success": False,
                        "error": "No flows match the provided criteria for this household.",
                    }
                )

            return json.dumps(
                {
                    "success": True,
                    "message": "Flows retrieved successfully.",
                    "flows": results,
                    "count": len(results),
                }
            )
        except Exception as exc:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Failed to retrieve flow information: {exc}",
                }
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "retrieve_flow_information",
                "description": (
                    "Retrieve automation flows for a specific household"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "Required household identifier to scope the flow lookup.",
                        },
                        "flow_name": {
                            "type": "string",
                            "description": "Required name of the flow.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional status filter ('enabled' or 'disabled'). Defaults to returning all statuses.",
                        },
                    },
                    "required": ["home_id", "flow_name"],
                },
            },
        }
