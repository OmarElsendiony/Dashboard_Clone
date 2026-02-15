import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool


class ListGroups(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: str,
        group_type: Optional[str] = None,
        include_member_count: Optional[bool] = False,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        if not channel_id:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'channel_id' is required."
            })

        if not isinstance(channel_id, str) or not channel_id.strip():
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: channel_id must be a non-empty string."
            })

        if include_member_count is None:
            include_member_count = False

        if not isinstance(include_member_count, bool):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: include_member_count must be a boolean."
            })

        groups = data.get("groups", {})
        group_members = data.get("group_members", {})

        if not isinstance(groups, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'groups' must be a dictionary"
            })

        if not isinstance(group_members, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'group_members' must be a dictionary"
            })

        valid_group_types = [
            "technical",
            "support",
            "admin",
            "Support_General",
            "Billing_Accounts",
            "Security_Response",
            "Engineering_Escalation",
        ]

        if group_type is not None:
            if not isinstance(group_type, str) or not group_type.strip():
                return json.dumps({
                    "success": False,
                    "error": "Invalid Argument: group_type must be a non-empty string when provided."
                })
            if group_type not in valid_group_types:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid Argument: group_type must be one of {valid_group_types}."
                })

        member_counts = {}
        if include_member_count:
            for m in group_members.values():
                if not isinstance(m, dict):
                    continue
                gid = m.get("group_id")
                if gid is None:
                    continue
                key = str(gid)
                member_counts[key] = member_counts.get(key, 0) + 1

        result = []

        for g in groups.values():
            if not isinstance(g, dict):
                continue

            if str(g.get("channel_id", "")).strip() != str(channel_id).strip():
                continue

            g_name_as_type = str(g.get("name", "")).strip()

            if group_type is not None:
                if g_name_as_type != group_type:
                    continue

            out = dict(g)

            # Map the conversion and remove the 'name' field
            out["group_type"] = g_name_as_type if g_name_as_type else "unknown"
            if "name" in out:
                del out["name"]

            if include_member_count:
                out["member_count"] = member_counts.get(str(g.get("group_id")), 0)

            result.append(out)

        if not result:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: No groups found for channel '{channel_id}'."
            })

        result.sort(
            key=lambda x: (
                str(x.get("group_type", "")).lower(),
                str(x.get("group_id", ""))
            )
        )

        return json.dumps({
            "success": True,
            "channel_id": channel_id,
            "group_type": group_type,
            "groups": result,
            "returned_count": len(result),
            "message": f"Groups retrieved successfully for channel {channel_id}."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_groups",
                "description": (
                    "Retrieves all support and operational groups mapped to a specific channel."
                    "PURPOSE: Helps identify valid routing and escalation groups that can be assigned to tickets or incidents."
                    "WHEN TO USE: When determining available queues for assignment, escalation, or workload distribution within a channel."
                    "RETURNS: A sorted list of groups, using group_type (converted from name), optionally filtered by group type and enriched with member count details."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "Channel identifier whose associated groups should be listed."
                        },
                        "group_type": {
                            "type": "string",
                            "enum": [
                                "technical",
                                "support",
                                "admin",
                                "Support_General",
                                "Billing_Accounts",
                                "Security_Response",
                                "Engineering_Escalation"
                            ],
                            "description": "Restrict results to a specific group type or category (optional)."
                        },
                        "include_member_count": {
                            "type": "boolean",
                            "description": "Include the number of members in each returned group (optional)."
                        }
                    },
                    "required": ["channel_id"]
                }
            }
        }
