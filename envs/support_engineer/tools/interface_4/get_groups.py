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
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return json.dumps({
                    "success": bool(False),
                    "error": str("Wrong data format"),
                })
        if not isinstance(data, dict):
            return json.dumps({
                "success": bool(False),
                "error": str("Wrong data format"),
            })

        groups = data.get("groups", {})

        results = []
        for group in groups.values():
            if group_id is not None and int(group.get("group_id", 0)) != int(group_id):
                continue

            if name is not None and name.lower() not in str(group.get("name") or "").lower():
                continue

            if channel_id is not None and str(group.get("channel_id", "")) != str(channel_id):
                continue

            results.append({
                "group_id": int(group.get("group_id", 0)),
                "name": str(group.get("name", "")),
                "channel_id": str(group.get("channel_id", "")),
            })

        return json.dumps({
            "success": bool(True),
            "groups": results,
            "count": int(len(results)),
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Lists support groups, optionally filtered by identifier, name, or channel.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "group_id": {
                            "type": "integer",
                            "description": "Filter by group identifier.",
                        },
                        "channel_id": {
                            "type": "string",
                            "description": "Filter by associated channel identifier.",
                        },
                        "name": {
                            "type": "string",
                            "description": "Filter by group name substring (case-insensitive).",
                            "enum": ["technical", "support"],
                        },
                    },
                    "required": [],
                },
            },
        }
