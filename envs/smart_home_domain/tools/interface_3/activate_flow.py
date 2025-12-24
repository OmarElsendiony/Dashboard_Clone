import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class ActivateFlow(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        home_id: str,
        flow_name: str,
    ) -> str:
        """Activate an automation flow for a household."""
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
                        "error": "Missing flows collection in the dataset.",
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

            home_id_clean = home_id.strip()
            flow_name_clean = flow_name.strip().lower()

            target_flow = None
            for record in routines.values():
                if not isinstance(record, dict):
                    continue
                if str(record.get("home_id", "")).strip() != home_id_clean:
                    continue
                if str(record.get("routine_name", "")).strip().lower() != flow_name_clean:
                    continue
                target_flow = record
                break

            if target_flow is None:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Flow not found for the provided home_id and flow_name.",
                    }
                )

            if str(target_flow.get("status", "")).strip().lower() == "enabled":
                return json.dumps(
                    {
                        "success": True,
                        "message": f"Flow '{target_flow.get('routine_name')}' is already enabled.",
                        "flow": {
                            "flow_id": target_flow.get("routine_id"),
                            "flow_name": target_flow.get("routine_name"),
                            "status": target_flow.get("status"),
                            "home_id": target_flow.get("home_id"),
                        },
                    }
                )

            target_flow["status"] = "enabled"
            target_flow["updated_at"] = "2025-12-19T23:59:00"

            return json.dumps(
                {
                    "success": True,
                    "message": f"Flow '{target_flow.get('routine_name')}' enabled successfully.",
                    "flow": {
                        "flow_id": target_flow.get("routine_id"),
                        "flow_name": target_flow.get("routine_name"),
                        "status": target_flow.get("status"),
                        "home_id": target_flow.get("home_id"),
                        "updated_at": target_flow.get("updated_at"),
                    },
                }
            )
        except Exception as exc:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Failed to activate flow: {exc}",
                }
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "activate_flow",
                "description": (
                    "Enable (activate) an automation flow identified by home_id and flow_name. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "home_id": {
                            "type": "string",
                            "description": "Required household identifier for the flow.",
                        },
                        "flow_name": {
                            "type": "string",
                            "description": "Required name of the flow to enable.",
                        },
                    },
                    "required": ["home_id", "flow_name"],
                },
            },
        }
