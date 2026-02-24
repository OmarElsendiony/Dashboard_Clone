import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool

class UpdateTicket(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        new_description: Optional[str] = None,
        new_status: Optional[str] = None,
        new_title: Optional[str] = None,
        new_priority: Optional[str] = None,
        new_assigned_to: Optional[str] = None,
        add_tag_ids: Optional[List[int]] = None,
        remove_tag_ids: Optional[List[int]] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        if not ticket_id:
            return json.dumps({
                "success": False,
                "error": "Missing required argument: 'ticket_id' is required."
            })

        ticket_id = str(ticket_id).strip()

        if (
            new_description is None
            and new_status is None
            and new_title is None
            and new_priority is None
            and new_assigned_to is None
            and add_tag_ids is None
            and remove_tag_ids is None
        ):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: At least one update field must be provided."
            })

        if new_description is not None and not isinstance(new_description, str):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: new_description must be a string when provided."
            })

        if new_title is not None and not isinstance(new_title, str):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: new_title must be a string when provided."
            })

        valid_statuses = [
            "archived",
            "deleted",
            "closed",
            "resolved",
            "open"
        ]

        if new_status is not None:
            new_status = str(new_status).strip().lower()
            if new_status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid Argument: new_status must be one of {valid_statuses}."
                })

        valid_priorities = ["P0", "P1", "P2", "P3"]

        if new_priority is not None:
            new_priority = str(new_priority).strip().upper()
            if new_priority not in valid_priorities:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid Argument: new_priority must be one of {valid_priorities}."
                })

        if new_assigned_to is not None and (not isinstance(new_assigned_to, str) or not new_assigned_to.strip()):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: new_assigned_to must be a non-empty string when provided."
            })

        add_ids: List[int] = []
        if add_tag_ids is not None:
            if not isinstance(add_tag_ids, list):
                return json.dumps({
                    "success": False,
                    "error": "Invalid Argument: add_tag_ids must be a list when provided."
                })
            for raw in add_tag_ids:
                try:
                    add_ids.append(int(str(raw)))
                except Exception:
                    return json.dumps({
                        "success": False,
                        "error": "Invalid Argument: add_tag_ids must contain only integers."
                    })

        remove_ids: List[int] = []
        if remove_tag_ids is not None:
            if not isinstance(remove_tag_ids, list):
                return json.dumps({
                    "success": False,
                    "error": "Invalid Argument: remove_tag_ids must be a list when provided."
                })
            for raw in remove_tag_ids:
                try:
                    remove_ids.append(int(str(raw)))
                except Exception:
                    return json.dumps({
                        "success": False,
                        "error": "Invalid Argument: remove_tag_ids must contain only integers."
                    })

        tickets = data.get("tickets", {})
        if not isinstance(tickets, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'tickets' must be a dictionary"
            })

        target_ticket = None
        for k, v in tickets.items():
            if isinstance(v, dict) and str(v.get("ticket_id", "")).strip() == ticket_id:
                target_ticket = v
                break

        if target_ticket is None:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: ticket_id '{ticket_id}' not found."
            })

        current_status = str(target_ticket.get("status", "")).lower()

        if new_status is not None:
            if new_status == "open" and current_status in ["archived", "deleted", "resolved"]:
                return json.dumps({
                    "success": False,
                    "error": "Policy Violation",
                    "message": f"Cannot change status from '{current_status}' to 'open'. Only 'closed' tickets can be reopened."
                })

        has_field_updates = any([
            new_description is not None,
            new_title is not None,
            new_priority is not None,
            new_assigned_to is not None,
            add_tag_ids is not None,
            remove_tag_ids is not None
        ])

        if has_field_updates and current_status in ["archived", "deleted", "closed", "resolved"]:
            if not (current_status == "closed" and new_status == "open"):
                return json.dumps({
                    "success": False,
                    "error": "Policy Violation",
                    "message": f"Cannot modify core fields or tags of a ticket with status '{current_status}'. Ticket must be 'open' to be edited."
                })

        tag_ops = (len(add_ids) > 0) or (len(remove_ids) > 0)
        tags = data.get("tags", {})
        ticket_tags = data.get("ticket_tags", {})

        tag_id_set = set()
        if tag_ops:
            if not isinstance(tags, dict):
                return json.dumps({
                    "success": False,
                    "error": "Invalid data format: 'tags' must be a dictionary for tag operations"
                })

            for k, v in tags.items():
                try:
                    tag_id_set.add(str(int(str(k))))
                except Exception:
                    if str(k).strip():
                        tag_id_set.add(str(k).strip())

                if isinstance(v, dict) and v.get("tag_id") is not None:
                    tag_id_set.add(str(v.get("tag_id")))

            for tid in add_ids:
                if str(tid) not in tag_id_set:
                    return json.dumps({
                        "success": False,
                        "error": f"Not Found Error: tag_id '{tid}' to add not found."
                    })

            for tid in remove_ids:
                if str(tid) not in tag_id_set:
                    return json.dumps({
                        "success": False,
                        "error": f"Not Found Error: tag_id '{tid}' to remove not found."
                    })

            if not isinstance(ticket_tags, (dict, list)):
                return json.dumps({
                    "success": False,
                    "error": "Invalid data format: 'ticket_tags' must be a dictionary or list for tag operations"
                })

        existing_pairs = set()
        next_ticket_tag_key = 1

        if tag_ops and isinstance(ticket_tags, dict):
            numeric_keys = []
            for k in ticket_tags.keys():
                try:
                    numeric_keys.append(int(str(k)))
                except Exception:
                    continue
            next_ticket_tag_key = (max(numeric_keys) + 1) if numeric_keys else (len(ticket_tags) + 1)

            for row in ticket_tags.values():
                if not isinstance(row, dict):
                    continue
                tid = str(row.get("ticket_id", ""))
                tag_id = row.get("tag_id")
                if tid and tag_id is not None:
                    existing_pairs.add((tid, str(tag_id)))

        if tag_ops and isinstance(ticket_tags, list):
            for row in ticket_tags:
                if not isinstance(row, dict):
                    continue
                tid = str(row.get("ticket_id", ""))
                tag_id = row.get("tag_id")
                if tid and tag_id is not None:
                    existing_pairs.add((tid, str(tag_id)))

        timestamp = "2026-02-02 23:59:00"

        tags_added = 0
        tags_removed = 0

        if tag_ops and len(remove_ids) > 0:
            remove_set = set((ticket_id, str(tag_id)) for tag_id in remove_ids)

            if isinstance(ticket_tags, dict):
                keys_to_delete = []
                for k, row in ticket_tags.items():
                    if not isinstance(row, dict):
                        continue
                    pair = (str(row.get("ticket_id", "")), str(row.get("tag_id", "")))
                    if pair in remove_set:
                        keys_to_delete.append(k)

                for k in keys_to_delete:
                    try:
                        row = ticket_tags.get(k)
                        if isinstance(row, dict):
                            pair = (str(row.get("ticket_id", "")), str(row.get("tag_id", "")))
                            if pair in existing_pairs:
                                existing_pairs.discard(pair)
                        del ticket_tags[k]
                        tags_removed += 1
                    except Exception:
                        continue

            if isinstance(ticket_tags, list):
                new_list = []
                for row in ticket_tags:
                    if not isinstance(row, dict):
                        new_list.append(row)
                        continue
                    pair = (str(row.get("ticket_id", "")), str(row.get("tag_id", "")))
                    if pair in remove_set:
                        if pair in existing_pairs:
                            existing_pairs.discard(pair)
                        tags_removed += 1
                        continue
                    new_list.append(row)
                ticket_tags[:] = new_list

        if tag_ops and len(add_ids) > 0:
            for tag_id in add_ids:
                pair = (ticket_id, str(tag_id))
                if pair in existing_pairs:
                    continue

                if isinstance(ticket_tags, dict):
                    key = str(next_ticket_tag_key)
                    next_ticket_tag_key += 1
                    ticket_tags[key] = {
                        "ticket_id": ticket_id,
                        "tag_id": int(tag_id),
                    }
                    existing_pairs.add(pair)
                    tags_added += 1

                if isinstance(ticket_tags, list):
                    ticket_tags.append({
                        "ticket_id": ticket_id,
                        "tag_id": int(tag_id),
                    })
                    existing_pairs.add(pair)
                    tags_added += 1

        is_change_detected = False

        if new_description is not None and target_ticket.get("description") != new_description:
            target_ticket["description"] = new_description
            is_change_detected = True

        if new_status is not None and target_ticket.get("status") != new_status:
            target_ticket["status"] = new_status
            is_change_detected = True
            if target_ticket["status"] == "resolved":
                target_ticket["resolved_at"] = timestamp
            if target_ticket["status"] == "closed":
                target_ticket["closed_at"] = timestamp

        if new_title is not None and target_ticket.get("title") != new_title:
            target_ticket["title"] = new_title
            is_change_detected = True

        if new_priority is not None and target_ticket.get("priority") != new_priority:
            target_ticket["priority"] = new_priority
            is_change_detected = True

        if new_assigned_to is not None and target_ticket.get("assigned_to") != new_assigned_to:
            target_ticket["assigned_to"] = new_assigned_to.strip()
            is_change_detected = True

        if tag_ops and (tags_added > 0 or tags_removed > 0):
            is_change_detected = True

        if is_change_detected:
            target_ticket["updated_at"] = timestamp
            return json.dumps({
                "success": True,
                "ticket": target_ticket,
                "tags_added": int(tags_added),
                "tags_removed": int(tags_removed),
                "message": f"Ticket '{ticket_id}' updated successfully."
            })
        else:
            return json.dumps({
                "success": False,
                "error": "No update Detected",
                "message": f"No-Op: Ticket '{ticket_id}' already has the provided values. No update performed."
            })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_ticket",
                "description": (
                    "Updates a specific support ticket by modifying its core fields or its associated tags.\n"
                    " Purpose: Ensures accurate ticket state management by modifying titles, descriptions, status, priority, assignments, and relevant categorization tags for a single ticket record.\n"
                    " When to use: Use this tool when you need to change one or multiple properties on an existing ticket, such as closing a resolved ticket, updating its priority during triage, reassigning it to another agent, editing its description, or adding/removing contextual tags.\n"
                    " Returns: Returns a JSON string containing a success boolean, the updated ticket dictionary object, the count of tags added/removed, and a success message. Fails if no fields are provided to update, if the ticket is terminal and field updates are attempted, or if the provided ticket ID does not exist."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The unique identifier of the ticket to update."
                        },
                        "new_description": {
                            "type": "string",
                            "description": "The updated description text for the ticket (optional)."
                        },
                        "new_status": {
                            "type": "string",
                            "enum": [
                                "archived",
                                "deleted",
                                "closed",
                                "resolved",
                                "open"
                            ],
                            "description": "The new status value to apply to the ticket. Policy prohibits changing 'archived', 'deleted', or 'resolved' tickets back to 'open'. Only 'closed' tickets can be reopened (optional)."
                        },
                        "new_title": {
                            "type": "string",
                            "description": "The updated title string for the ticket (optional)."
                        },
                        "new_priority": {
                            "type": "string",
                            "enum": ["P0", "P1", "P2", "P3"],
                            "description": "The new priority level to assign to the ticket (optional)."
                        },
                        "new_assigned_to": {
                            "type": "string",
                            "description": "The identifier of the user to assign the ticket to (optional)."
                        },
                        "add_tag_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "A list of integer tag IDs to associate with this ticket (optional)."
                        },
                        "remove_tag_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "A list of integer tag IDs to remove from this ticket (optional)."
                        }
                    },
                    "required": ["ticket_id"]
                }
            }
        }
