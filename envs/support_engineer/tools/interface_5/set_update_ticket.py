import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class SetUpdateTicket(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        updates: Dict[str, Any],
    ) -> str:

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        if not ticket_id:
            return json.dumps({"success": False, "error": "Ticket ID is required"})

        if not updates:
            return json.dumps({"success": False, "error": "At least one update field is required"})

        if not isinstance(updates, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'updates' must be a dict"})

        tickets = data.get("tickets", {})
        users = data.get("users", {})
        # Validate ticket existence
        if ticket_id not in tickets:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Ticket with ID '{ticket_id}' does not exist",
                }
            )
        ticket = tickets[ticket_id]
        # Valid fields that can be updated
        valid_update_fields = {
            "status",
            "assigned_to",
            "priority",
            "title",
            "description",
            "escalation_reason",
            "kb_article_link",
            "incident_timestamp",
            "resolved_at",
            "closed_at",
        }
        # Apply updates
        copy_ticket = ticket.copy()
        for field, value in updates.items():
            if field in valid_update_fields:
                # validate enums
                if field == "status":
                    if value not in ["open", "in_progress", "awaiting_info", "resolved", "closed"]:
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"Invalid status value '{value}', must be one of ['open', 'in_progress', 'awaiting_info', 'resolved', 'closed']",
                            }
                        )
                if field == "priority":
                    if value not in ["P0", "P1", "P2", "P3", "P4"]:
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"Invalid priority value '{value}', must be one of ['P0', 'P1', 'P2', 'P3', 'P4']",
                            }
                        )
                if field == "assigned_to":
                    user = users.get(value, None)
                    if not user:
                        return json.dumps({"Success": False, "error": f"User with ID {value} not found"})
                copy_ticket[field] = value
            else:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid update field '{field}'",
                    }
                )
        # update the updated_at timestamp
        copy_ticket["updated_at"] = "2026-02-02 23:59:00"
        tickets[ticket_id] = copy_ticket
        return json.dumps(
            {
                "success": True,
                "ticket": copy_ticket,
            }
        )


    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "set_update_ticket",
                "description": "Update ticket fields including assignment, status, priority, title, description, escalation reason, KB article links, timestamps, and resolution/closure dates. Use this to modify ticket properties during triage, assignment, status transitions, escalation handling, or resolution workflows. At least one field must be provided to update.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The ID of the ticket to be updated.",
                        },
                        "updates": {
                            "type": "object",
                            "description": "A dictionary of fields to update on the ticket.",
                            "properties": {
                                "status": {"type": "string", "description": "The new status of the ticket.", "enum": ["open", "in_progress", "awaiting_info", "resolved", "closed"]},
                                "assigned_to": {"type": ["string", "null"], "description": "The user ID of the person assigned to the ticket."},
                                "priority": {"type": "string", "description": "The priority level of the ticket.", "enum": ["P0", "P1", "P2", "P3", "P4"]},
                                "title": {"type": "string", "description": "The new title of the ticket."},
                                "description": {"type": "string", "description": "The new description of the ticket."},
                                "escalation_reason": {"type": ["string", "null"], "description": "The reason for escalation of the ticket."},
                                "kb_article_link": {"type": "string", "description": "The link to the knowledge base article related to the ticket."},
                                "incident_timestamp": {"type": ["string", "null"], "description": "The timestamp of when the incident occurred."},
                                "resolved_at": {"type": ["string", "null"], "description": "The timestamp of when the ticket was resolved."},
                                "closed_at": {"type": ["string", "null"], "description": "The timestamp of when the ticket was closed."},

                            },
                    },
                    },
                    "required": ["ticket_id", "updates"],
                },
            },
        }
