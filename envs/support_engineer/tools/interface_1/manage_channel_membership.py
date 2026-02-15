import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class ManageChannelMembership(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: str,
        user_id: str,
        action: str,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        channels = data.get("channels", {})
        users = data.get("users", {})
        channel_members = data.get("channel_members", {})

        if not action:
            return json.dumps({"success": False, "error": "Missing Argument: 'action' is required."})

        valid_actions = ["add", "remove"]
        if action not in valid_actions:
             return json.dumps({
                "success": False,
                "error": f"Invalid Argument: action must be one of {valid_actions}."
            })

        if not channel_id:
             return json.dumps({"success": False, "error": "Missing Argument: 'channel_id' is required."})
        if not user_id:
             return json.dumps({"success": False, "error": "Missing Argument: 'user_id' is required."})

        if str(channel_id) not in channels:
            return json.dumps({"success": False, "error": f"Not Found Error: Channel ID '{channel_id}' not found."})

        if str(user_id) not in users:
            return json.dumps({"success": False, "error": f"Not Found Error: User ID '{user_id}' not found."})

        existing_membership_key = None
        for key, member_record in channel_members.items():
            if str(member_record.get("channel_id")) == str(channel_id) and \
               str(member_record.get("user_id")) == str(user_id):
                existing_membership_key = key
                break

        timestamp = "2026-02-02 23:59:00"

        if action == "add":
            if existing_membership_key:
                return json.dumps({
                    "success": False,
                    "error": f"Action Failed: User '{user_id}' is already a member of channel '{channel_id}'."
                })

            try:
                new_key = str(max(int(k) for k in channel_members.keys() if k.isdigit()) + 1)
            except ValueError:
                new_key = str(len(channel_members) + 1)

            new_record = {
                "channel_id": str(channel_id),
                "user_id": str(user_id),
                "joined_at": timestamp
            }

            channel_members[new_key] = new_record

            return json.dumps({
                "success": True,
                "action": "add",
                "message": f"User '{user_id}' successfully added to channel '{channel_id}'."
            })

        if action == "remove":
            if not existing_membership_key:
                return json.dumps({
                    "success": False,
                    "error": f"Action Failed: User '{user_id}' is not a member of channel '{channel_id}'."
                })

            del channel_members[existing_membership_key]

            return json.dumps({
                "success": True,
                "action": "remove",
                "message": f"User '{user_id}' successfully removed from channel '{channel_id}'."
            })

        return json.dumps({"success": False, "error": "Unknown logic path."})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "manage_channel_membership",
                "description": (
                    "Manages the roster of a communication channel. "
                    "PURPOSE: Adds or removes specific users from a Slack channel. "
                    "WHEN TO USE: 1) 'add': Critical for Incident Swarms (P0). 2) 'remove': To revoke access when a user leaves the team or project. "
                    "RETURNS: JSON confirmation of the roster update."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "REQUIRED. The unique identifier of the target channel."
                        },
                        "user_id": {
                            "type": "string",
                            "description": "REQUIRED. The unique identifier of the user to add or remove."
                        },
                        "action": {
                            "type": "string",
                            "enum": ["add", "remove"],
                            "description": "REQUIRED. The operation to perform."
                        }
                    },
                    "required": ["channel_id", "user_id", "action"]
                }
            }
        }
