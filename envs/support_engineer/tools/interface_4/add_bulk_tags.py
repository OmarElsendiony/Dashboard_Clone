import json
from typing import Any, Dict, List
from tau_bench.envs.tool import Tool


class AddBulkTags(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_tags_mapping: List[Dict[str, Any]],
    ) -> str:
        if isinstance(data, str):
            data = json.loads(data)
        if isinstance(ticket_tags_mapping, str):
            ticket_tags_mapping = json.loads(ticket_tags_mapping)
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        if ticket_tags_mapping is None:
            return json.dumps(
                {"success": False, "error": "ticket_tags_mapping is required"}
            )
        if not isinstance(ticket_tags_mapping, list):
            return json.dumps(
                {"success": False, "error": "ticket_tags_mapping has wrong format"}
            )
        if not ticket_tags_mapping:
            return json.dumps(
                {"success": False, "error": "ticket_tags_mapping must not be empty"}
            )

        tickets = data.get("tickets", {})
        tags = data.get("tags", {})
        ticket_tags = data.get("ticket_tags")
        if ticket_tags is None:
            ticket_tags = {}
            data["ticket_tags"] = ticket_tags

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
            if ticket_id is None or ticket_id == "":
                return json.dumps(
                    {"success": False, "error": "ticket_id is required in each mapping"}
                )
            if tag_names is None:
                return json.dumps(
                    {"success": False, "error": "tag_names is required in each mapping"}
                )
            if not isinstance(tag_names, list):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"tag_names must be a list for ticket \"{ticket_id}\"",
                    }
                )
            if str(ticket_id) not in tickets:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Ticket with id \"{ticket_id}\" not found",
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
                        "error": f"Tag \"{tag_name}\" not found. Valid tags: {', '.join(sorted(valid_tag_names))}",
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
                                "ticket_id": str(ticket_id),
                                "tag_name": str(tag_name),
                                "reason": "already_exists",
                            }
                        )
                        break
                if not already_exists:
                    new_ticket_tag = {
                        "ticket_id": str(ticket_id),
                        "tag_id": int(tag_id) if isinstance(tag_id, (int, float)) else str(tag_id),
                    }
                    ticket_tags[str(next_id)] = new_ticket_tag
                    added_tags.append(
                        {
                            "ticket_id": str(ticket_id),
                            "tag_id": int(tag_id) if isinstance(tag_id, (int, float)) else str(tag_id),
                        }
                    )
                    next_id += 1

        out_added = [
            {"ticket_id": str(a["ticket_id"]), "tag_id": a["tag_id"]}
            for a in added_tags
        ]
        out_skipped = [
            {
                "ticket_id": str(s["ticket_id"]),
                "tag_name": str(s["tag_name"]),
                "reason": str(s["reason"]),
            }
            for s in skipped_tags
        ]
        return json.dumps(
            {
                "success": True,
                "added_tags": out_added,
                "added_count": int(len(added_tags)),
                "skipped_tags": out_skipped,
                "skipped_count": int(len(skipped_tags)),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_bulk_tags",
                "description": "Adds tags to multiple tickets in batch for categorization and tracking.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_tags_mapping": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "description": "A single mapping of one ticket to a list of tag names.",
                                "properties": {
                                    "ticket_id": {
                                        "type": "string",
                                        "description": "Ticket identifier.",
                                    },
                                    "tag_names": {
                                        "type": "array",
                                        "items": {
                                            "type": "string",
                                            "enum": [
                                                "awaiting_customer",
                                                "duplicate",
                                                "high_priority",
                                                "medium_priority",
                                                "low_priority",
                                                "has_documentation",
                                            ],
                                            "description": "One tag name to add to the ticket.",
                                        },
                                        "description": "Array of tag names to add to this ticket.",
                                    },
                                },
                                "required": ["ticket_id", "tag_names"],
                            },
                            "description": "Array of ticket-to-tags mappings, e.g. [{\"ticket_id\": \"123\", \"tag_names\": [\"high_priority\"]}].",
                        },
                    },
                    "required": ["ticket_tags_mapping"],
                },
            },
        }
