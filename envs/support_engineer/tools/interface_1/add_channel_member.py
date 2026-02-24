import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class AddChannelMember(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        channel_id: str,
        user_id: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not channel_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'channel_id' is required."})

        if not user_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'user_id' is required."})

        channel_id = str(channel_id).strip()
        user_id = str(user_id).strip()

        channels = data.get("channels", {})
        users = data.get("users", {})
        channel_members = data.get("channel_members", {})

        if channel_id not in channels:
            return json.dumps({"success": False, "error": f"Not Found Error: channel_id '{channel_id}' not found."})

        if user_id not in users:
            return json.dumps({"success": False, "error": f"Not Found Error: user_id '{user_id}' not found."})

        for member in channel_members.values():
            if isinstance(member, dict):
                if str(member.get("channel_id", "")).strip() == channel_id and str(member.get("user_id", "")).strip() == user_id:
                    return json.dumps({"success": False, "error": f"Duplicate Error: user_id '{user_id}' is already a member of channel_id '{channel_id}'."})

        max_mem_id = 0
        for k in channel_members.keys():
            try:
                num = int(str(k))
                if num > max_mem_id:
                    max_mem_id = num
            except ValueError:
                continue

        new_mem_id = str(max_mem_id + 1)
        timestamp = "2026-02-02 23:59:00"

        new_member_record = {
            "channel_id": channel_id,
            "user_id": user_id,
            "joined_at": timestamp
        }

        channel_members[new_mem_id] = new_member_record

        return json.dumps({
            "success": True,
            "member_record": new_member_record,
            "message": f"User '{user_id}' added to channel '{channel_id}' successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_channel_member",
                "description": (
                    " Adds a specific user (personnel) to an existing communication channel.\n"
                    " Purpose: Facilitates the expansion of channel membership, specifically to invite necessary stakeholders like the Incident Commander and Tech Lead to newly created swarm channels.\n"
                    " When to use: Use this tool in the 'Coordinate Incident Swarms' SOP step or whenever a workflow requires adding specific personnel to a target channel to assist in incident resolution.\n"
                    " Returns: Returns a JSON string containing a success boolean, the newly created channel member dictionary object, and a success message. Fails if the channel or user does not exist, or if the user is already a member."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "The unique identifier of the target channel."
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The unique identifier of the user (e.g., Tech Lead or Incident Commander) to add to the channel."
                        }
                    },
                    "required": ["channel_id", "user_id"]
                }
            }
        }
