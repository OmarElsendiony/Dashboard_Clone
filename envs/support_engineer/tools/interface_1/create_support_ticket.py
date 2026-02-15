import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool


class CreateSupportTicket(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        subject: str,
        description: str,
        requester_id: str,
        status: Optional[str] = "open",
        priority: Optional[str] = "P3",
        tag_ids: Optional[List[int]] = None,
        assigned_to: Optional[str] = None,
        ingestion_channel: Optional[str] = "Web",
        incident_timestamp: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        if not subject:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'subject' is required."
            })

        if not description:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'description' is required."
            })

        if not requester_id:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'requester_id' is required."
            })

        if not isinstance(subject, str) or not subject.strip():
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: subject must be a non-empty string."
            })

        if not isinstance(description, str) or not description.strip():
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: description must be a non-empty string."
            })

        if not isinstance(requester_id, str) or not requester_id.strip():
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: requester_id must be a non-empty string."
            })

        tickets = data.get("tickets", {})
        customers = data.get("customers", {})
        users = data.get("users", {})
        tags = data.get("tags", {})
        ticket_tags = data.get("ticket_tags", {})

        if not isinstance(tickets, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'tickets' must be a dictionary"
            })

        if not isinstance(customers, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'customers' must be a dictionary"
            })

        requester_key = str(requester_id).strip()
        requester_found = False

        if requester_key in customers:
            requester_found = True
        else:
            for v in customers.values():
                if isinstance(v, dict) and str(v.get("customer_id", "")).strip() == requester_key:
                    requester_found = True
                    break

        if not requester_found:
            return json.dumps({
                "success": False,
                "error": f"Foreign Key Error: requester_id '{requester_id}' not found."
            })

        for existing_ticket in tickets.values():
            if isinstance(existing_ticket, dict):
                if (str(existing_ticket.get("customer_id")) == requester_key and
                    existing_ticket.get("title") == subject.strip() and
                    existing_ticket.get("status") not in ["closed", "resolved", "archived"]):
                    return json.dumps({
                        "success": False,
                        "error": "Similar supportticket Detected",
                        "message": f"No-Op: A ticket with the subject '{subject}' already exists for requester {requester_id} and is currently {existing_ticket.get('status')}."
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

        final_status = "open"
        if status is not None:
            if not isinstance(status, str) or not status.strip():
                return json.dumps({
                    "success": False,
                    "error": "Invalid Argument: status must be a non-empty string when provided."
                })
            final_status = status.strip()
        else:
            final_status = "open"

        if final_status not in valid_statuses:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: status must be one of {valid_statuses}."
            })

        valid_priorities = ["P0", "P1", "P2", "P3", "P4"]

        final_priority = "P3"
        if priority is not None:
            if not isinstance(priority, str) or not priority.strip():
                return json.dumps({
                    "success": False,
                    "error": "Invalid Argument: priority must be a non-empty string when provided."
                })
            final_priority = priority.strip().upper()
        else:
            final_priority = "P3"

        if final_priority not in valid_priorities:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: priority must be one of {valid_priorities}."
            })

        valid_ingestion_channels = ["Phone", "Chat", "Web", "Email", "Slack"]

        final_ingestion_channel = "Web"
        if ingestion_channel is not None:
            if not isinstance(ingestion_channel, str) or not ingestion_channel.strip():
                return json.dumps({
                    "success": False,
                    "error": "Invalid Argument: ingestion_channel must be a non-empty string when provided."
                })
            ic_norm = ingestion_channel.strip().lower()
            ic_map = {
                "phone": "Phone",
                "chat": "Chat",
                "web": "Web",
                "email": "Email",
                "slack": "Slack",
            }
            final_ingestion_channel = ic_map.get(ic_norm, ingestion_channel.strip())
        else:
            final_ingestion_channel = "Web"

        if final_ingestion_channel not in valid_ingestion_channels:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: ingestion_channel must be one of {valid_ingestion_channels}."
            })

        if assigned_to is not None:
            if not isinstance(assigned_to, str) or not assigned_to.strip():
                return json.dumps({
                    "success": False,
                    "error": "Invalid Argument: assigned_to must be a non-empty string when provided."
                })
            if isinstance(users, dict) and str(assigned_to).strip() not in users:
                return json.dumps({
                    "success": False,
                    "error": f"Foreign Key Error: assigned_to '{assigned_to}' not found."
                })

        normalized_tag_ids: List[int] = []
        if tag_ids is not None:
            if not isinstance(tag_ids, list):
                return json.dumps({
                    "success": False,
                    "error": "Invalid Argument: tag_ids must be a list when provided."
                })
            for raw in tag_ids:
                try:
                    normalized_tag_ids.append(int(str(raw)))
                except Exception:
                    return json.dumps({
                        "success": False,
                        "error": "Invalid Argument: tag_ids must contain only integers."
                    })

        if len(normalized_tag_ids) > 0:
            if not isinstance(tags, dict):
                return json.dumps({
                    "success": False,
                    "error": "Invalid data format: 'tags' must be a dictionary to attach tags."
                })

            existing_tag_ids = set()
            for k, v in tags.items():
                try:
                    existing_tag_ids.add(int(str(k)))
                except Exception:
                    pass
                if isinstance(v, dict) and v.get("tag_id") is not None:
                    try:
                        existing_tag_ids.add(int(str(v.get("tag_id"))))
                    except Exception:
                        pass

            for tid in normalized_tag_ids:
                if tid not in existing_tag_ids:
                    return json.dumps({
                        "success": False,
                        "error": f"Not Found Error: tag_id '{tid}' not found."
                    })

            if not isinstance(ticket_tags, (dict, list)):
                return json.dumps({
                    "success": False,
                    "error": "Invalid data format: 'ticket_tags' must be a dictionary or list to attach tags."
                })

        numeric_ids = []
        for k in tickets.keys():
            try:
                numeric_ids.append(int(str(k)))
            except Exception:
                continue

        for v in tickets.values():
            if isinstance(v, dict) and v.get("ticket_id") is not None:
                try:
                    numeric_ids.append(int(str(v.get("ticket_id"))))
                except Exception:
                    continue

        new_ticket_int = (max(numeric_ids) + 1) if numeric_ids else (len(tickets) + 1)
        new_ticket_id = str(new_ticket_int)

        existing_ticket_numbers = set()
        for v in tickets.values():
            if isinstance(v, dict):
                tn = v.get("ticket_number")
                if tn is not None:
                    existing_ticket_numbers.add(str(tn))

        base_ticket_number = f"ZD-{new_ticket_id}"
        ticket_number = base_ticket_number
        if ticket_number in existing_ticket_numbers:
            suffix = 1
            while f"{base_ticket_number}-{suffix}" in existing_ticket_numbers:
                suffix += 1
            ticket_number = f"{base_ticket_number}-{suffix}"

        timestamp = "2026-02-02 23:59:00"

        new_ticket = {
            "ticket_id": new_ticket_id,
            "ticket_number": ticket_number,
            "customer_id": requester_key,
            "assigned_to": assigned_to.strip() if isinstance(assigned_to, str) and assigned_to.strip() else "",
            "title": subject.strip(),
            "description": description.strip(),
            "priority": final_priority,
            "status": final_status,
            "escalation_reason": "",
            "ingestion_channel": final_ingestion_channel,
            "incident_timestamp": incident_timestamp.strip() if isinstance(incident_timestamp, str) and incident_timestamp.strip() else "",
            "created_at": timestamp,
            "updated_at": timestamp,
            "resolved_at": "",
            "closed_at": "",
        }

        tickets[new_ticket_id] = new_ticket

        created_tag_links = 0
        if len(normalized_tag_ids) > 0:
            existing_pairs = set()

            if isinstance(ticket_tags, dict):
                numeric_keys = []
                for k in ticket_tags.keys():
                    try:
                        numeric_keys.append(int(str(k)))
                    except Exception:
                        continue
                next_key = (max(numeric_keys) + 1) if numeric_keys else (len(ticket_tags) + 1)

                for row in ticket_tags.values():
                    if isinstance(row, dict):
                        tid = str(row.get("ticket_id", ""))
                        tag_id_row = row.get("tag_id")
                        if tid and tag_id_row is not None:
                            existing_pairs.add((tid, str(tag_id_row)))

                for tid in normalized_tag_ids:
                    pair = (new_ticket_id, str(tid))
                    if pair in existing_pairs:
                        continue
                    ticket_tags[str(next_key)] = {
                        "ticket_id": new_ticket_id,
                        "tag_id": int(tid),
                    }
                    next_key += 1
                    created_tag_links += 1

            if isinstance(ticket_tags, list):
                for row in ticket_tags:
                    if isinstance(row, dict):
                        tid = str(row.get("ticket_id", ""))
                        tag_id_row = row.get("tag_id")
                        if tid and tag_id_row is not None:
                            existing_pairs.add((tid, str(tag_id_row)))

                for tid in normalized_tag_ids:
                    pair = (new_ticket_id, str(tid))
                    if pair in existing_pairs:
                        continue
                    ticket_tags.append({
                        "ticket_id": new_ticket_id,
                        "tag_id": int(tid),
                    })
                    created_tag_links += 1

        return json.dumps({
            "success": True,
            "ticket": new_ticket,
            "tags_attached": created_tag_links,
            "message": f"Ticket '{ticket_number}' created successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_support_ticket",
                "description": (
                    "Creates a new support ticket to capture a newly reported customer request, issue, or incident."
                    "PURPOSE: Establishes a structured, trackable record with initial triage metadata for routing, tracking, and reporting."
                    "WHEN TO USE: When handling new inbound requests, logging incidents, or converting external reports into support tickets."
                    "RETURNS: The created ticket record including assigned metadata and linked classification tags."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subject": {
                            "type": "string",
                            "description": "Ticket subject."
                        },
                        "description": {
                            "type": "string",
                            "description": "Ticket description."
                        },
                        "requester_id": {
                            "type": "string",
                            "description": "Requester identifier."
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
                            "description": "Initial ticket status (optional )"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["P0", "P1", "P2", "P3", "P4"],
                            "description": "Initial ticket priority (optional )"
                        },
                        "tag_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Classification tag identifiers to attach to the new ticket (optional )"
                        },
                        "assigned_to": {
                            "type": "string",
                            "description": "Initial assignee identifier for the ticket (optional )"
                        },
                        "ingestion_channel": {
                            "type": "string",
                            "enum": ["Phone", "Chat", "Web", "Email", "Slack"],
                            "description": "Ingestion channel for the ticket (optional )"
                        },
                        "incident_timestamp": {
                            "type": "string",
                            "description": "Incident timestamp associated with the ticket (optional )"
                        }
                    },
                    "required": ["subject", "description", "requester_id"]
                }
            }
        }
