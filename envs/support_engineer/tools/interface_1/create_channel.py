import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateChannel(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        agent_id: str,
        name: str,
        channel_type: Optional[str] = "general",
        description: Optional[str] = None,
        ticket_id: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not agent_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'agent_id' is required."})

        if not name:
            return json.dumps({"success": False, "error": "Missing Argument: 'name' is required."})

        agent_id = str(agent_id).strip()
        name = str(name).strip()

        users = data.get("users", {})
        channels = data.get("channels", {})
        channel_members = data.get("channel_members", {})

        if agent_id not in users:
            return json.dumps({"success": False, "error": f"Authorization Error: agent_id '{agent_id}' not found."})

        timestamp = "2026-02-02 23:59:00"
        valid_types = ["incident", "security", "general", "accounts", "sla", "public", "private", "direct"]

        c_type = str(channel_type).strip().lower() if channel_type else "general"
        if c_type not in valid_types:
            return json.dumps({"success": False, "error": f"Invalid Argument: channel_type must be one of {valid_types}."})

        for c in channels.values():
            if isinstance(c, dict) and str(c.get("name", "")).strip().lower() == name.lower():
                 return json.dumps({"success": False, "error": f"Duplicate Error: Channel with name '{name}' already exists."})

        max_id = 0
        for k in channels.keys():
            try:
                num = int(str(k))
                if num > max_id:
                    max_id = num
            except ValueError:
                continue

        for v in channels.values():
            if isinstance(v, dict):
                try:
                    num = int(str(v.get("channel_id", "0")))
                    if num > max_id:
                        max_id = num
                except ValueError:
                    continue

        new_channel_id = str(max_id + 1)

        new_channel = {
            "channel_id": new_channel_id,
            "channel_type": c_type,
            "name": name,
            "description": str(description).strip() if description else "",
            "ticket_id": str(ticket_id).strip() if ticket_id else "",
            "status": "active",
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        channels[new_channel_id] = new_channel

        max_mem_id = 0
        for k in channel_members.keys():
            try:
                num = int(str(k))
                if num > max_mem_id:
                    max_mem_id = num
            except ValueError:
                continue

        new_mem_id = str(max_mem_id + 1)

        channel_members[new_mem_id] = {
            "channel_id": new_channel_id,
            "user_id": agent_id,
            "joined_at": timestamp
        }

        return json.dumps({
            "success": True,
            "channel": new_channel,
            "message": f"Channel '{name}' created successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_channel",
                "description": (
                    "Creates a new Slack communication channel and automatically adds the creating agent as the first member.\n"
                    " Purpose: Automates the provisioning of communication channels to ensure teams can collaborate effectively during support escalations, swarms, or operational events.\n"
                    " When to use: Use this tool when a workflow requires spinning up a new dedicated channel (e.g., for an incident swarm, security event, or general collaboration), linking it to an optional ticket.\n"
                    " Returns: Returns a JSON string containing a success boolean, the newly created channel dictionary object (with its generated channel_id), and a success message text. Fails if the agent_id is invalid or if a channel with the same name already exists."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Agent identifier performing the channel creation."
                        },
                        "name": {
                            "type": "string",
                            "description": "The name of the new channel (must be unique)."
                        },
                        "channel_type": {
                            "type": "string",
                            "enum": ["incident", "security", "general", "accounts", "sla", "public", "private", "direct"],
                            "description": "Channel type classification (default is 'general')."
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description or topic for the channel."
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "Optional associated ticket identifier for linking the channel to a support ticket."
                        }
                    },
                    "required": ["agent_id", "name"]
                }
            }
        }
