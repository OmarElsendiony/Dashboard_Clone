import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ManageChannel(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        agent_id: str,
        channel_id: Optional[str] = None,
        name: Optional[str] = None,
        channel_type: Optional[str] = None,
        description: Optional[str] = None,
        ticket_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not action:
            return json.dumps({"success": False, "error": "Missing Argument: 'action' is required."})

        if not agent_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'agent_id' is required."})

        if not isinstance(action, str):
            return json.dumps({"success": False, "error": "Invalid Argument: action must be a non-empty string."})

        valid_actions = ["create", "join", "update"]
        if action not in valid_actions:
             return json.dumps({"success": False, "error": f"Invalid Argument: action must be one of {valid_actions}."})

        users = data.get("users", {})
        channels = data.get("channels", {})
        channel_members = data.get("channel_members", {})

        if agent_id not in users:
            return json.dumps({"success": False, "error": f"Authorization Error: agent_id '{agent_id}' not found."})

        timestamp = "2026-02-02T23:59:00"
        valid_types = ["incident", "security", "general", "accounts", "sla", "public", "private", "direct"]

        if action == "create":
            if not name:
                return json.dumps({"success": False, "error": "Invalid Argument: name is required for 'create'."})

            c_type = channel_type if channel_type else "general"
            if c_type not in valid_types:
                return json.dumps({"success": False, "error": f"Invalid Argument: channel_type must be one of {valid_types}."})

            for c in channels.values():
                if c.get("name") == name and c.get("channel_type") == c_type:
                     return json.dumps({"success": False, "error": "Duplicate channel detected."})

            try:
                new_id = str(max([int(k) for k in channels.keys() if k.isdigit()] or [0]) + 1)
            except ValueError:
                new_id = str(len(channels) + 1)

            new_channel = {
                "channel_id": new_id,
                "channel_type": c_type,
                "name": name,
                "description": description or "",
                "ticket_id": ticket_id or "",
                "status": "active",
                "created_at": timestamp,
                "updated_at": timestamp,
                "channel_users": [agent_id]
            }

            channels[new_id] = new_channel

            try:
                mem_id = str(max([int(k) for k in channel_members.keys() if k.isdigit()] or [0]) + 1)
            except ValueError:
                mem_id = str(len(channel_members) + 1)

            channel_members[mem_id] = {
                "channel_id": new_id,
                "user_id": agent_id,
                "joined_at": timestamp
            }

            return json.dumps({"success": True, "action": "create", "channel": new_channel})

        if action == "join":
            if not channel_id or channel_id not in channels:
                return json.dumps({"success": False, "error": f"Not Found: channel_id '{channel_id}' not found."})

            current_members = [m.get("user_id") for m in channel_members.values() if m.get("channel_id") == channel_id]

            if agent_id in current_members:
                return json.dumps({"success": False, "error": "Agent is already a member."})

            try:
                mem_id = str(max([int(k) for k in channel_members.keys() if k.isdigit()] or [0]) + 1)
            except ValueError:
                mem_id = str(len(channel_members) + 1)

            channel_members[mem_id] = {
                "channel_id": channel_id,
                "user_id": agent_id,
                "joined_at": timestamp
            }

            channels[channel_id]["channel_users"] = current_members + [agent_id]

            return json.dumps({"success": True, "action": "join", "channel": channels[channel_id]})

        if action == "update":
            if not channel_id or channel_id not in channels:
                return json.dumps({"success": False, "error": f"Not Found: channel_id '{channel_id}' not found."})

            channel = channels[channel_id]
            changed = False

            if name and name != channel.get("name"):
                channel["name"] = name
                changed = True

            if channel_type:
                if channel_type not in valid_types:
                    return json.dumps({"success": False, "error": f"Invalid Argument: channel_type must be one of {valid_types}."})
                if channel_type != channel.get("channel_type"):
                    channel["channel_type"] = channel_type
                    changed = True

            if description is not None and description != channel.get("description"):
                channel["description"] = description
                changed = True

            if ticket_id is not None and ticket_id != channel.get("ticket_id"):
                channel["ticket_id"] = ticket_id
                changed = True

            if not changed:
                return json.dumps({"success": False, "error": "No changes detected."})

            channel["updated_at"] = timestamp
            return json.dumps({"success": True, "action": "update", "channel": channel})

        return json.dumps({"success": False, "error": "Invalid action."})


    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "manage_channel",
                "description": (
                    "Executes Slack channel lifecycle actions for collaboration and incident coordination."
                    "PURPOSE: Automates the creation, expansion, and naming of communication channels to ensure teams can collaborate effectively during support escalations or operational events."
                    "WHEN TO USE: When a workflow requires spinning up a new channel for a security event, adding a specific agent to an ongoing discussion, or updating a channel's name to match standardized naming conventions or a corrected scope."
                    "RETURNS: The channel and membership outcome."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["create", "join", "update"],
                            "description": "Channel lifecycle action to execute."
                        },
                        "agent_id": {
                            "type": "string",
                            "description": "Agent identifier performing the channel operation."
                        },
                        "channel_id": {
                            "type": "string",
                            "description": "Target channel identifier. Required when action is 'join' or 'update' (optional )"
                        },
                        "name": {
                            "type": "string",
                            "description": "Channel name to use when creating a new channel. Required when action is 'create' (optional )"
                        },
                        "channel_type": {
                            "type": "string",
                            "enum": ["incident", "security", "general", "accounts", "sla", "public", "private", "direct"],
                            "description": "Channel type classification for new channels (optional )"
                        },
                        "description": {
                            "type": "string",
                            "description": "Channel description text for new channels (optional )"
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "Associated ticket identifier for linking a channel to a ticket (optional )"
                        }
                    },
                    "required": ["action", "agent_id"]
                }
            }
        }
