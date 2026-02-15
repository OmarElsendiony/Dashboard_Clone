import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateSpace(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        name: str,
        description:str,
        creator_id: str,
        channel_type: str = "general"
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        def generate_id(table: Dict[str, Any]) -> str:
            return str(max([int(k) for k in table.keys()], default=0) + 1)
        tickets = data.get("tickets", {})
        users = data.get("users", {})

        if not ticket_id:
            return json.dumps({"success": False, "error": "Ticket ID is required"})

        if not name:
            return json.dumps({"success": False, "error": "Space name is required"})

        if not description:
            return json.dumps({"success": False, "error": "Space description is required"})

        if not creator_id:
            return json.dumps({"success": False, "error": "Creator ID is required"})

        # validate the creator_id
        if creator_id not in users:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{creator_id}' does not exist"
            })
        # validate the ticket_id
        if ticket_id not in tickets:
            return json.dumps({
                "success": False,
                "error": f"Ticket with ID '{ticket_id}' does not exist"
            })
        # Validation: Enums
        valid_channel_types = ['incident', 'security', 'general', 'accounts', 'sla', 'public', 'private', 'direct']
        if channel_type not in valid_channel_types:
            return json.dumps({
                "success": False,
                "error": f"Invalid channel_type. Must be one of {valid_channel_types}"
            })
        spaces = data.get("channels", {})
        space_members = data.get("channel_members", {})
        new_space_id = generate_id(spaces)
        new_space_member_id = generate_id(space_members)
        new_space = {
            "channel_id": new_space_id,
            "name": str(name),
            "description": str(description),
            "channel_type": channel_type,
            "created_at": "2026-02-02 23:59:00",
            "updated_at": "2026-02-02 23:59:00",
            "ticket_id": str(ticket_id),
            "status": "active"
        }
        # add self to membership
        space_members[new_space_member_id] = {
            "channel_id": new_space_id,
            "user_id": str(creator_id),
            "joined_at": "2026-02-02 23:59:00",
        }
        spaces[new_space_id] = new_space
        data["channels"] = spaces
        data["channel_members"] = space_members
        return json.dumps({"success": True, "new_channel": new_space, "members": space_members[new_space_member_id]})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_space",
                "description": "Establishes a new collaborative communication channel dedicated to a specific ticket. use when a new issue arises that requires focused discussion and coordination among relevant team members.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The ID of the ticket for which the space is being created."
                        },
                        "name": {
                            "type": "string",
                            "description": "The name of the new space."
                        },
                        "description": {
                            "type": "string",
                            "description": "A description of the new space."
                        },
                        "channel_type": {
                            "type": "string",
                            "description": "The type of channel to create.",
                            "enum": ['incident', 'security', 'general', 'accounts', 'sla', 'public', 'private', 'direct']
                        },
                        "creator_id": {
                            "type": "string",
                            "description": "The ID of the user creating the space."
                        }
                    },
                    "required": ["ticket_id", "name", "description", "creator_id"]
                }
            }
        }
