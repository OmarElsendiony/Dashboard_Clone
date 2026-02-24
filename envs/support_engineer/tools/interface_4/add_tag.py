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

        if ticket_id is None or (isinstance(ticket_id, str) and not ticket_id.strip()):
            return json.dumps({
                "success": bool(False),
                "error": str("ticket_id is required"),
            })
        if tag_name is None or (isinstance(tag_name, str) and not tag_name.strip()):
            return json.dumps({
                "success": bool(False),
                "error": str("tag_name is required"),
            })

        ticket_id = str(ticket_id)
        tag_name = str(tag_name)

        tickets = data.get("tickets", {})
        tags = data.get("tags", {})
        ticket_tags = data.get("ticket_tags", {})

        if ticket_id not in tickets:
            return json.dumps({
                "success": bool(False),
                "error": str(f"Ticket with id '{ticket_id}' not found"),
            })

        tag_info = None
        for tag in tags.values():
            if tag.get("tag_name") == tag_name:
                tag_info = tag
                break

        if not tag_info:
            valid_tag_names = [tag.get("tag_name") for tag in tags.values()]
            return json.dumps({
                "success": bool(False),
                "error": str(f"Tag '{tag_name}' not found. Valid tags: {', '.join(sorted(valid_tag_names))}"),
            })

        tag_id = tag_info.get("tag_id")

        for ticket_tag in ticket_tags.values():
            if (
                str(ticket_tag.get("ticket_id")) == ticket_id
                and ticket_tag.get("tag_id") == tag_id
            ):
                return json.dumps({
                    "success": bool(False),
                    "error": str(f"Tag '{tag_name}' is already added to ticket '{ticket_id}'"),
                })

        if ticket_tags:
            max_id = max(int(k) for k in ticket_tags.keys())
            new_ticket_tag_id = str(max_id + 1)
        else:
            new_ticket_tag_id = "1"

        new_ticket_tag = {
            "ticket_id": str(ticket_id),
            "tag_id": int(tag_id),
        }

        ticket_tags[new_ticket_tag_id] = new_ticket_tag

        return json.dumps({
            "success": bool(True),
            "ticket_tag": {
                "ticket_id": str(new_ticket_tag["ticket_id"]),
                "tag_id": int(new_ticket_tag["tag_id"]),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_tag",
                "description": "Adds a single tag to a ticket for categorization and tracking.",
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
