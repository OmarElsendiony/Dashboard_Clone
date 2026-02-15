import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetGroups(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        group_id: Optional[int] = None,
        channel_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        groups = data.get("groups", {})

        results = []
        for group in groups.values():
            if group_id is not None and str(group.get("group_id")) != str(group_id):
                continue

            if name is not None and name.lower() not in (group.get("name") or "").lower():
                continue

            if channel_id is not None and str(group.get("channel_id")) != str(
                channel_id
            ):
                continue

            results.append(group)

        return json.dumps({"success": True, "groups": results, "count": len(results)})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "List support groups, optionally filtered by identifier, name, or channel.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "group_id": {
                            "type": "integer",
                            "description": "Filter by group identifier",
                        },
                        "channel_id": {
                            "type": "string",
                            "description": "Filter by associated channel identifier",
                        },
                        "name": {
                            "type": "string",
                            "description": "Filter by group name substring (case-insensitive)",
                            "enum": ['technical', 'support'],
                        },
                    },
                    "required": [],
                },
            },
        }
