import json
from typing import Any, Dict, List
from tau_bench.envs.tool import Tool


class AddBulkTags(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_tags_mapping: List[Dict[str, Any]],
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not ticket_tags_mapping:
            return json.dumps(
                {"success": False, "error": "ticket_tags_mapping is required"}
            )

        if not isinstance(ticket_tags_mapping, list):
            return json.dumps(
                {"success": False, "error": "ticket_tags_mapping must be a list"}
            )

        tickets = data.get("tickets", {})
        tags = data.get("tags", {})
        ticket_tags = data.get("ticket_tags", {})

        all_tag_names = set()
        for mapping in ticket_tags_mapping:
            if not isinstance(mapping, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Each item in ticket_tags_mapping must be a dictionary",
                    }
                )

            ticket_id = mapping.get("ticket_id")
            tag_names = mapping.get("tag_names")

            if not ticket_id:
                return json.dumps(
                    {"success": False, "error": "ticket_id is required in each mapping"}
                )

            if not tag_names:
                return json.dumps(
                    {"success": False, "error": "tag_names is required in each mapping"}
                )

            if not isinstance(tag_names, list):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"tag_names must be a list for ticket '{ticket_id}'",
                    }
                )

            if str(ticket_id) not in tickets:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Ticket with id '{ticket_id}' not found",
                    }
                )

            for tag_name in tag_names:
                all_tag_names.add(tag_name)

        tag_info_map = {}
        for tag_name in all_tag_names:
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

            tag_info_map[tag_name] = tag_info

        added_tags = []
        skipped_tags = []

        if ticket_tags:
            next_id = max(int(k) for k in ticket_tags.keys()) + 1
        else:
            next_id = 1

        for mapping in ticket_tags_mapping:
            ticket_id = mapping.get("ticket_id")
            tag_names = mapping.get("tag_names")

            for tag_name in tag_names:
                tag_info = tag_info_map[tag_name]
                tag_id = tag_info.get("tag_id")

                already_exists = False
                for ticket_tag in ticket_tags.values():
                    if (
                        str(ticket_tag.get("ticket_id")) == str(ticket_id)
                        and ticket_tag.get("tag_id") == tag_id
                    ):
                        already_exists = True
                        skipped_tags.append(
                            {
                                "ticket_id": ticket_id,
                                "tag_name": tag_name,
                                "reason": "already_exists",
                            }
                        )
                        break

                if not already_exists:
                    new_ticket_tag = {
                        "ticket_id": ticket_id,
                        "tag_id": tag_id,
                    }

                    ticket_tags[str(next_id)] = new_ticket_tag
                    added_tags.append(new_ticket_tag)
                    next_id += 1

        return json.dumps(
            {
                "success": True,
                "added_tags": added_tags,
                "added_count": len(added_tags),
                "skipped_tags": skipped_tags,
                "skipped_count": len(skipped_tags),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_bulk_tags",
                "description": "Add tags to multiple tickets in batch for categorization and tracking.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_tags_mapping": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "ticket_id": {
                                        "type": "string",
                                        "description": "Ticket identifier",
                                    },
                                    "tag_names": {
                                        "type": "array",
                                        "items": {
                                            "type": "string",
                                            "enum": ["awaiting_customer", "duplicate", "high_priority", "medium_priority", "low_priority", "has_documentation"],
                                        },
                                        "description": "Array of tag names to add to this ticket",
                                    },
                                },
                                "required": ["ticket_id", "tag_names"],
                            },
                            "description": "Array of ticket-to-tags mappings e.g. [{'ticket_id': '123', 'tag_names': ['bug', 'incident']}]",
                        },
                    },
                    "required": ["ticket_tags_mapping"],
                },
            },
        }
