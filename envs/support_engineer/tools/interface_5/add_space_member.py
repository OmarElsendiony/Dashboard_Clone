import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class AddSpaceMember(Tool):
    @staticmethod
    def invoke(
            data: Dict[str, Any],
            channel_id: str,
            user_id: str
        ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not channel_id:
            return json.dumps({"success": False, "error": "Channel ID is required"})

        if not user_id:
            return json.dumps({"success": False, "error": "User ID is required"})

        spaces = data.get("channels", {})
        space_members = data.get("channel_members", {})
        users = data.get("users", {})
        if channel_id not in spaces:
            return json.dumps({
                "success": False,
                "error": f"Channel with ID '{channel_id}' does not exist"
            })
        if user_id not in users:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{user_id}' does not exist"
            })
        # Check if user is already a member of the space
        existing_member = None
        for member_id, member_info in space_members.items():
            if member_info["channel_id"] == channel_id and member_info["user_id"] == user_id:
                existing_member = member_id
                break
        if existing_member is not None:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{user_id}' is already a member of channel '{channel_id}'"
            })
        # Generate new member ID and add to space members
        def generate_id(table: Dict[str, Any]) -> str:
            return str(max([int(k) for k in table.keys()], default=0) + 1)
        new_member_id = generate_id(space_members)
        new_member = {
            "channel_id": str(channel_id),
            "user_id": str(user_id),
            "joined_at": "2026-02-02 23:59:00",
        }
        space_members[new_member_id] = new_member
        data["channel_members"] = space_members
        return json.dumps({"success": True, "new_member": new_member, "channel_members": space_members[new_member_id]})



    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_space_member",
                "description": "Grants a user access to a specific communication channel by adding them to the channel's membership list. It should be used to manage workspace permissions, ensuring that the relevant personnel are added to ticket-specific channels. ",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel_id": {
                            "type": "string",
                            "description": "The ID of the communication channel."
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user to be added as a member."
                        }
                    },
                    "required": ["channel_id", "user_id"]
                }
            }
        }
