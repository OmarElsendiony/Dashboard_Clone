import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool

class MergeTickets(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        primary_ticket_id: str,
        ticket_ids_to_merge: List[str],
        close_merged_tickets: Optional[bool] = True,
        add_merge_comment: Optional[bool] = True,
        merged_by: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not primary_ticket_id:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'primary_ticket_id' is required."
            })

        if not ticket_ids_to_merge:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'ticket_ids_to_merge' is required."
            })

        if not isinstance(primary_ticket_id, str) or not primary_ticket_id.strip():
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: primary_ticket_id must be a non-empty string."
            })

        if not isinstance(ticket_ids_to_merge, list) or len(ticket_ids_to_merge) == 0:
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: ticket_ids_to_merge must be a non-empty list."
            })

        if close_merged_tickets is None:
            close_merged_tickets = True
        if add_merge_comment is None:
            add_merge_comment = True

        if not isinstance(close_merged_tickets, bool):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: close_merged_tickets must be a boolean."
            })

        if not isinstance(add_merge_comment, bool):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: add_merge_comment must be a boolean."
            })

        if merged_by is not None and (not isinstance(merged_by, str) or not merged_by.strip()):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: merged_by must be a non-empty string when provided."
            })

        tickets = data.get("tickets", {})
        if not isinstance(tickets, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'tickets' must be a dictionary"
            })

        ticket_comments = data.get("ticket_comments", {})
        ticket_notes = data.get("ticket_notes", {})
        ticket_tags = data.get("ticket_tags", {})
        tags = data.get("tags", {})
        customer_messages = data.get("customer_messages", {})
        escalations = data.get("escalations", {})
        customer_feedback = data.get("customer_feedback", {})
        emails = data.get("emails", {})
        channel_messages = data.get("channel_messages", {})

        def_format_ok = True
        invalid_ids = []

        primary_raw = primary_ticket_id.strip()
        primary_upper = primary_raw.upper()
        if primary_upper.startswith("ZD-") and primary_upper[3:].isdigit():
            primary_canon = primary_upper[3:]
        elif primary_raw.isdigit():
            primary_canon = primary_raw
        else:
            def_format_ok = False
            invalid_ids.append(primary_ticket_id)

        normalized_inputs = []
        canonical_seen = set()
        duplicates = []
        includes_primary = False

        for raw in ticket_ids_to_merge:
            val = str(raw).strip()
            if not val:
                def_format_ok = False
                invalid_ids.append(str(raw))
                continue

            up = val.upper()
            if up.startswith("ZD-") and up[3:].isdigit():
                canon = up[3:]
            elif val.isdigit():
                canon = val
            else:
                def_format_ok = False
                invalid_ids.append(val)
                continue

            if canon == primary_canon:
                includes_primary = True

            if canon in canonical_seen:
                duplicates.append(val)
            else:
                canonical_seen.add(canon)
                normalized_inputs.append((val, canon))

        if not def_format_ok:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: invalid ticket_id format(s): {sorted(set(invalid_ids))}. Valid formats are numeric ticket numbers (e.g., '4921') or 'ZD-<number>'."
            })

        if includes_primary:
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: ticket_ids_to_merge must not include the primary ticket."
            })

        if duplicates:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: duplicate ticket references detected: {sorted(set(duplicates))}."
            })

        timestamp = "2026-02-02 23:59:00"

        primary_ticket = None
        for v in tickets.values():
            if isinstance(v, dict):
                tid = str(v.get("ticket_id", "")).strip()
                tnum = str(v.get("ticket_number", "")).strip()
                if tid == primary_canon or tnum == primary_canon:
                    primary_ticket = v
                    break

        if primary_ticket is None:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: primary_ticket_id '{primary_ticket_id}' not found."
            })

        primary_key = str(primary_ticket.get("ticket_id", "")).strip()

        closed_dup_tag_id = None
        for t_id, t_data in tags.items():
            if t_data.get("tag_name") == "closed_duplicate":
                closed_dup_tag_id = int(t_id)
                break

        if closed_dup_tag_id is None:
            try:
                numeric_ids = [int(k) for k in tags.keys()]
                new_tag_id = max(numeric_ids) + 1 if numeric_ids else 1
            except:
                new_tag_id = len(tags) + 1

            closed_dup_tag_id = new_tag_id
            tags[str(new_tag_id)] = {
                "tag_id": new_tag_id,
                "tag_name": "closed_duplicate",
                "description": "System tag for tickets closed via merge."
            }

        merge_tickets = []
        resolved_ticket_ids = set()
        missing = []

        for original, canon in normalized_inputs:
            found = None
            for v in tickets.values():
                if not isinstance(v, dict):
                    continue
                tid = str(v.get("ticket_id", "")).strip()
                tnum = str(v.get("ticket_number", "")).strip()
                if tid == canon or tnum == canon:
                    found = v
                    break

            if found is None:
                missing.append(original)
            else:
                real_id = str(found.get("ticket_id", "")).strip()
                if real_id in resolved_ticket_ids:
                    duplicates.append(original)
                else:
                    resolved_ticket_ids.add(real_id)
                    merge_tickets.append(found)

        if missing:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: ticket_id(s) {missing} not found."
            })

        if duplicates:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: duplicate merge targets detected after resolution: {sorted(set(duplicates))}."
            })

        valid_to_process = []
        for t in merge_tickets:
            curr_id = str(t.get("ticket_id", ""))

            already_merged = False
            if t.get("status") in ["solved", "closed"]:
                for link in ticket_tags.values():
                    if str(link.get("ticket_id")) == curr_id:
                        tid = link.get("tag_id")
                        if tid == closed_dup_tag_id or str(tid) == str(closed_dup_tag_id):
                            already_merged = True
                            break

            if not already_merged:
                valid_to_process.append(t)

        if len(merge_tickets) > 0 and len(valid_to_process) == 0:
            return json.dumps({
                "success": False,
                "error": "No-Op: All provided tickets are already merged and closed as duplicates."
            })

        tables_ticket_id = [
            ticket_comments,
            ticket_notes,
            ticket_tags,
            customer_messages,
            escalations,
            customer_feedback,
            emails,
        ]

        for t in valid_to_process:
            old_id = str(t.get("ticket_id", "")).strip()
            if not old_id:
                continue

            for table in tables_ticket_id:
                rows = []
                if isinstance(table, dict):
                    rows = list(table.values())
                elif isinstance(table, list):
                    rows = table

                for row in rows:
                    if isinstance(row, dict) and str(row.get("ticket_id", "")) == old_id:
                        row["ticket_id"] = primary_key
                        if "updated_at" in row:
                            row["updated_at"] = timestamp

            rows_cm = []
            if isinstance(channel_messages, dict):
                rows_cm = list(channel_messages.values())
            elif isinstance(channel_messages, list):
                rows_cm = channel_messages

            for row in rows_cm:
                if isinstance(row, dict) and str(row.get("related_ticket_id", "")) == old_id:
                    row["related_ticket_id"] = primary_key
                    if "updated_at" in row:
                        row["updated_at"] = timestamp

            if close_merged_tickets:

                t["status"] = "closed"
                if "closed_at" in t:
                    t["closed_at"] = timestamp
                if "updated_at" in t:
                    t["updated_at"] = timestamp

                link_exists = False
                for link in ticket_tags.values():
                    if str(link.get("ticket_id")) == old_id and str(link.get("tag_id")) == str(closed_dup_tag_id):
                        link_exists = True
                        break

                if not link_exists:
                    try:
                        numeric_keys = [int(k) for k in ticket_tags.keys() if str(k).isdigit()]
                        new_link_key = str(max(numeric_keys) + 1) if numeric_keys else "1"
                    except:
                        new_link_key = str(len(ticket_tags) + 1)

                    ticket_tags[new_link_key] = {
                        "ticket_id": old_id,
                        "tag_id": closed_dup_tag_id
                    }

        if "updated_at" in primary_ticket:
            primary_ticket["updated_at"] = timestamp

        if add_merge_comment:
            if not isinstance(ticket_comments, dict):
                return json.dumps({
                    "success": False,
                    "error": "Invalid data format: 'ticket_comments' must be a dictionary to add a merge comment."
                })

            numeric_ids = []
            for k in ticket_comments.keys():
                try:
                    numeric_ids.append(int(str(k)))
                except Exception:
                    continue

            new_comment_id = str(max(numeric_ids) + 1) if numeric_ids else str(len(ticket_comments) + 1)

            merged_list_text = ", ".join(sorted(resolved_ticket_ids))
            by_text = f" by {merged_by}" if merged_by else ""
            comment_text = f"Merged tickets into {primary_key}: {merged_list_text}{by_text}."

            ticket_comments[new_comment_id] = {
                "comment_id": new_comment_id,
                "ticket_id": primary_key,
                "sender_id": str(merged_by) if merged_by else "",
                "message": comment_text,
                "is_public": False,
                "created_at": timestamp,
                "updated_at": timestamp
            }

        return json.dumps({
            "success": True,
            "primary_ticket": primary_ticket,
            "merged_ticket_ids": sorted(resolved_ticket_ids),
            "message": f"Tickets merged successfully into primary ticket {primary_ticket_id}."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "merge_tickets",
                "description": (
                    "Merges multiple support tickets into a single primary ticket to consolidate duplicates or related requests."
                    "PURPOSE: Ensures a single source of truth by combining duplicate or closely related tickets into one authoritative case."
                    "WHEN TO USE: After confirming that multiple tickets represent the same underlying issue during deduplication or triage workflows."
                    "RETURNS: The updated primary ticket and a list of successfully merged ticket IDs."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "primary_ticket_id": {
                            "type": "string",
                            "description": "Primary Zendesk ticket reference to keep. Valid formats: numeric ticket number (e.g., '4921') or 'ZD-<number>'."
                        },
                        "ticket_ids_to_merge": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Zendesk ticket references to merge into the primary ticket. Each entry must be unique and use a valid ticket format (e.g., '4921') or 'ZD-<number>'."
                        },
                        "close_merged_tickets": {
                            "type": "boolean",
                            "description": "Close merged tickets after reassignment (optional)."
                        },
                        "add_merge_comment": {
                            "type": "boolean",
                            "description": "Add an internal merge audit comment to the primary ticket (optional)."
                        },
                        "merged_by": {
                            "type": "string",
                            "description": "Identifier of the agent performing the merge (optional)."
                        }
                    },
                    "required": ["primary_ticket_id", "ticket_ids_to_merge"]
                }
            }
        }
