import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool


class BulkUpdateTickets(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_ids: List[str],
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        add_tag_ids: Optional[List[int]] = None,
        remove_tag_ids: Optional[List[int]] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        if not ticket_ids:
            return json.dumps({
                "success": False,
                "error": "Missing required argument: ticket_ids is required and must be a non-empty list."
            })

        if not isinstance(ticket_ids, list) or len(ticket_ids) == 0:
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: ticket_ids must be a non-empty list."
            })

        normalized_ticket_ids: List[str] = []
        seen = set()
        for raw in ticket_ids:
            tid = str(raw).strip()
            if not tid:
                continue
            if tid in seen:
                continue
            seen.add(tid)
            normalized_ticket_ids.append(tid)

        if len(normalized_ticket_ids) == 0:
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: ticket_ids must contain at least one valid ticket id."
            })

        if (
            status is None
            and priority is None
            and assigned_to is None
            and add_tag_ids is None
            and remove_tag_ids is None
        ):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: At least one update field must be provided."
            })

        if status is not None and (not isinstance(status, str) or not status.strip()):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: status must be a non-empty string when provided."
            })

        if priority is not None and (not isinstance(priority, str) or not priority.strip()):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: priority must be a non-empty string when provided."
            })

        if assigned_to is not None and (not isinstance(assigned_to, str) or not assigned_to.strip()):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: assigned_to must be a non-empty string when provided."
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

        valid_statuses = [
            "open",
            "closed",
            "pending",
            "resolved",
            "awaiting_info",
            "ready_for_investigation",
            "root_cause_identified",
            "in_progress",
            "fix_proposed",
            "fix_rejected",
            "pending_review",
            "pending_security_review",
            "escalated",
            "archived",
        ]

        if status is not None and status.strip() not in valid_statuses:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: status must be one of {valid_statuses}."
            })

        valid_priorities = ["P0", "P1", "P2", "P3", "P4"]

        if priority is not None and priority.strip() not in valid_priorities:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: priority must be one of {valid_priorities}."
            })

        tickets = data.get("tickets", {})
        if not isinstance(tickets, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'tickets' must be a dictionary"
            })

        ticket_by_id: Dict[str, Dict[str, Any]] = {}
        for k, v in tickets.items():
            if isinstance(v, dict):
                ticket_by_id[str(k)] = v
                if v.get("ticket_id") is not None:
                    ticket_by_id[str(v.get("ticket_id"))] = v

        missing = []
        target_tickets: List[Dict[str, Any]] = []
        for tid in normalized_ticket_ids:
            t = ticket_by_id.get(str(tid))
            if t is None:
                missing.append(tid)
            else:
                target_tickets.append(t)

        if missing:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: ticket_id(s) {missing} not found."
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
                        "error": f"Not Found Error: tag_id '{tid}' not found."
                    })

            for tid in remove_ids:
                if str(tid) not in tag_id_set:
                    return json.dumps({
                        "success": False,
                        "error": f"Not Found Error: tag_id '{tid}' not found."
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
            remove_set = set((tid, str(tag_id)) for tid in normalized_ticket_ids for tag_id in remove_ids)

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
            for tid in normalized_ticket_ids:
                for tag_id in add_ids:
                    pair = (str(tid), str(tag_id))
                    if pair in existing_pairs:
                        continue

                    if isinstance(ticket_tags, dict):
                        key = str(next_ticket_tag_key)
                        next_ticket_tag_key += 1
                        ticket_tags[key] = {
                            "ticket_id": str(tid),
                            "tag_id": int(tag_id),
                        }
                        existing_pairs.add(pair)
                        tags_added += 1

                    if isinstance(ticket_tags, list):
                        ticket_tags.append({
                            "ticket_id": str(tid),
                            "tag_id": int(tag_id),
                        })
                        existing_pairs.add(pair)
                        tags_added += 1

        updated_ticket_ids = []
        updated_tickets = []

        for t in target_tickets:
            tid = str(t.get("ticket_id", "")).strip()
            changed = False

            if status is not None:
                t["status"] = status.strip()
                changed = True
                if t["status"] == "resolved" and "resolved_at" in t:
                    t["resolved_at"] = timestamp
                if t["status"] == "closed" and "closed_at" in t:
                    t["closed_at"] = timestamp

            if priority is not None:
                t["priority"] = priority.strip()
                changed = True

            if assigned_to is not None:
                t["assigned_to"] = assigned_to.strip()
                changed = True

            if tag_ops:
                changed = True

            if changed:
                if "updated_at" in t:
                    t["updated_at"] = timestamp
                updated_ticket_ids.append(tid if tid else "")
                updated_tickets.append(t)

        updated_ticket_ids = [x for x in updated_ticket_ids if x]

        return json.dumps({
            "success": True,
            "tickets": updated_tickets,
            "updated_ticket_ids": updated_ticket_ids,
            "updated_count": len(updated_ticket_ids),
            "tags_added": tags_added,
            "tags_removed": tags_removed,
            "message": "Bulk ticket update completed successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "bulk_update_tickets",
                "description": (
                    "Performs bulk updates on multiple support tickets by applying the same changes across a selected set."
                    "PURPOSE: Ensures consistent ticket state management and efficient large-scale administrative or triage actions."
                    "WHEN TO USE: When multiple tickets require the same update such as status changes, tag updates, priority adjustments, or reassignment."
                    "RETURNS: A list of updated ticket records reflecting the applied bulk changes."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Ticket identifiers to update."
                        },
                        "status": {
                            "type": "string",
                            "enum": [
                                "open",
                                "closed",
                                "pending",
                                "resolved",
                                "awaiting_info",
                                "ready_for_investigation",
                                "root_cause_identified",
                                "in_progress",
                                "fix_proposed",
                                "fix_rejected",
                                "pending_review",
                                "pending_security_review",
                                "escalated",
                                "archived"
                            ],
                            "description": "New ticket status to apply (optional )"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["P0", "P1", "P2", "P3", "P4"],
                            "description": "New ticket priority to apply (optional )"
                        },
                        "assigned_to": {
                            "type": "string",
                            "description": "New assignee identifier to apply (optional )"
                        },
                        "add_tag_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Tag identifiers to add to each ticket (optional )"
                        },
                        "remove_tag_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Tag identifiers to remove from each ticket (optional )"
                        }
                    },
                    "required": ["ticket_ids"]
                }
            }
        }
