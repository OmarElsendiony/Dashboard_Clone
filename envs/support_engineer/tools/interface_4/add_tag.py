import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class AddTag(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        tag_name: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not ticket_id:
            return json.dumps({"success": False, "error": "ticket_id is required"})

        if not tag_name:
            return json.dumps({"success": False, "error": "tag_name is required"})

        tickets = data.get("tickets", {})
        tags = data.get("tags", {})
        ticket_tags = data.get("ticket_tags", {})

        if str(ticket_id) not in tickets:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Ticket with id '{ticket_id}' not found",
                }
            )

        tag_info = None
        for tag in tags.values():
            if tag.get("tag_name") == tag_name:
                tag_info = tag
                break

        if not tag_info:
            valid_tag_names = [tag.get("tag_name") for tag in tags.values()]
            return json.dumps(
                {
                    "success": False,
                    "error": f"Tag '{tag_name}' not found. Valid tags: {', '.join(sorted(valid_tag_names))}",
                }
            )

        tag_id = tag_info.get("tag_id")

        for ticket_tag in ticket_tags.values():
            if (
                str(ticket_tag.get("ticket_id")) == str(ticket_id)
                and ticket_tag.get("tag_id") == tag_id
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Tag '{tag_name}' is already added to ticket '{ticket_id}'",
                    }
                )

        if ticket_tags:
            max_id = max(int(k) for k in ticket_tags.keys())
            new_ticket_tag_id = str(max_id + 1)
        else:
            new_ticket_tag_id = "1"

        new_ticket_tag = {
            "ticket_id": ticket_id,
            "tag_id": tag_id,
        }

        ticket_tags[new_ticket_tag_id] = new_ticket_tag

        return json.dumps({"success": True, "ticket_tag": new_ticket_tag})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_tag",
                "description": "Add a single tag to a ticket for categorization and tracking.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket identifier to add the tag to",
                        },
                        "tag_name": {
                            "type": "string",
                            "description": "Name of the tag to add",
                            "enum": ["awaiting_customer", "duplicate", "high_priority", "medium_priority", "low_priority", "has_documentation"],
                        },
                    },
                    "required": ["ticket_id", "tag_name"],
                },
            },
        }
