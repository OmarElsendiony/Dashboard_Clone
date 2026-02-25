import json
from typing import Dict, Any
from tau_bench.envs.tool import Tool


class AddTagToTicket(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_number: str,
        tag_type: str,
        tag: str,
    ) -> str:
        if not ticket_number:
            return json.dumps({"error": "ticket_number is required"})

        if not tag_type:
            return json.dumps({"error": "tag_type is required"})

        if not tag:
            return json.dumps({"error": "tag is required"})

        valid_tags_by_type = {
            "issue_type": ("bug", "incident", "request", "query"),
            "impact_level": ("low", "medium", "high", "critical"),
            "priority": ("P1", "P2", "P3", "P4"),
            "queue": ("urgent_queue", "high_priority_queue", "standard_queue", "low_priority_queue"),
            "actionable": ("is_actionable", "is_not_actionable"),
        }

        if tag_type not in valid_tags_by_type:
            return json.dumps(
                {"error": f"Invalid tag_type '{tag_type}'. Must be one of: {', '.join(valid_tags_by_type.keys())}"}
            )

        valid_tags = valid_tags_by_type[tag_type]
        if tag not in valid_tags:
            return json.dumps(
                {"error": f"Invalid tag '{tag}' for tag_type '{tag_type}'. Must be one of: {', '.join(valid_tags)}"}
            )

        tickets = data.get("tickets", {})
        ticket_tags = data.get("ticket_tags", {})
        tags = data.get("tags", {})

        ticket_id = None
        ticket_details = None

        for t_id, t_details in tickets.items():
            if t_details.get("ticket_number") == ticket_number:
                ticket_id = t_id
                ticket_details = t_details
                break

        if not ticket_details:
            return json.dumps({"error": f"Ticket with number '{ticket_number}' not found"})

        # Create new tag in tags table
        new_tag_id = str(max(int(k) for k in tags.keys()) + 1) if tags else "1"
        tags[new_tag_id] = {
            "tag_name": str(tag),
            "tag_type": str(tag_type),
        }
        data["tags"] = tags

        # Link tag to ticket in ticket_tags
        new_key = str(max(int(k) for k in ticket_tags.keys()) + 1) if ticket_tags else "1"
        ticket_tags[new_key] = {
            "ticket_id": str(ticket_id),
            "tag_id": int(new_tag_id),
        }
        data["ticket_tags"] = ticket_tags

        return json.dumps({
            "success": True,
            "ticket_tag": {
                "ticket_id": str(ticket_id),
                "ticket_number": str(ticket_details["ticket_number"]),
                "tag_id": int(new_tag_id),
                "tag_name": str(tag),
                "tag_type": str(tag_type),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_tag_to_ticket",
                "description": "Adds a tag to an existing ticket in the ticketing system. It should be used when you need to associate a tag with a ticket.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_number": {
                            "type": "string",
                            "description": "The number of the ticket",
                        },
                        "tag_type": {
                            "type": "string",
                            "description": "The type of tag to add",
                            "enum": ["issue_type", "impact_level", "priority", "queue", "actionable"],
                        },
                        "tag": {
                            "type": "string",
                            "description": "The tag name to add to the ticket",
                        },
                    },
                    "required": ["ticket_number", "tag_type", "tag"],
                },
            },
        }