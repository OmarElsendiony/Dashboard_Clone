import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class EditTicket(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        description: Optional[str] = None,
        title: Optional[str] = None,
        escalation_reason: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-02 23:59:00"

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        if not ticket_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'ticket_id'"})

        tickets_dict = data.get("tickets", {})
        users_dict = data.get("users", {})

        ticket_id_str = str(ticket_id).strip()
        status_str = str(status).strip() if status else None
        priority_str = str(priority).strip() if priority else None
        assigned_to_str = str(assigned_to).strip() if assigned_to else None
        description_str = str(description).strip() if description else None
        title_str = str(title).strip() if title else None
        escalation_reason_str = (
            str(escalation_reason).strip() if escalation_reason else None
        )

        # Check at least one update parameter is provided
        if not any(
            [status, priority, assigned_to, description, title, escalation_reason]
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one field (status, priority, assigned_to, description, title, or escalation_reason) must be provided for update",
                }
            )

        if ticket_id_str not in tickets_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Ticket with ID '{ticket_id_str}' not found",
                }
            )

        ticket = tickets_dict[ticket_id_str]

        if not isinstance(ticket, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid ticket data structure for ticket ID '{ticket_id_str}'",
                }
            )

        valid_statuses = [
            "open",
            "closed",
            "resolved",
            "awaiting_info",
            "in_progress",
            "fix_proposed",
            "pending_review",
            "pending_security_review",
            "archived",
            "root_cause_identified"
            "resolved_pending_verification",
        ]

        if status_str and status_str not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status_str}'. Must be one of: {', '.join(valid_statuses)}",
                }
            )

        valid_priorities = ["P0", "P1", "P2", "P3"]

        if priority_str and priority_str not in valid_priorities:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid priority '{priority_str}'. Must be one of: {', '.join(valid_priorities)}",
                }
            )

        valid_escalation_reasons = [
            "code_bug",
            "infrastructure",
            "security",
            "data_corruption",
            "access_limitation",
        ]

        if (
            escalation_reason_str
            and escalation_reason_str not in valid_escalation_reasons
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid escalation_reason '{escalation_reason_str}'. Must be one of: {', '.join(valid_escalation_reasons)}",
                }
            )

        if assigned_to_str:
            if assigned_to_str not in users_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User with ID '{assigned_to_str}' not found",
                    }
                )

            assignee = users_dict[assigned_to_str]

            if not isinstance(assignee, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid user data structure for user ID '{assigned_to_str}'",
                    }
                )

            user_role = assignee.get("role")
            valid_roles = ["support_engineer", "technical_engineer"]

            if user_role not in valid_roles:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User '{assigned_to_str}' cannot be assigned tickets. User role must be one of: {', '.join(valid_roles)}",
                    }
                )

            user_status = assignee.get("status")
            if user_status != "active":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User '{assigned_to_str}' is not active and cannot be assigned tickets",
                    }
                )

        current_status = ticket.get("status")
        if current_status and current_status == "archived":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Ticket '{ticket_id_str}' is archived and cannot be processed",
                }
            )
        changes = {}

        if status_str:
            if status_str == "resolved" and current_status != "resolved":
                ticket["resolved_at"] = timestamp
                changes["resolved_at"] = timestamp
            elif status_str == "closed" and current_status != "closed":
                ticket["closed_at"] = timestamp
                changes["closed_at"] = timestamp
                if not ticket.get("resolved_at"):
                    ticket["resolved_at"] = timestamp
                    changes["resolved_at"] = timestamp

            ticket["status"] = status_str
            changes["status"] = {"old": current_status, "new": status_str}

        if priority_str:
            old_priority = ticket.get("priority")
            ticket["priority"] = priority_str
            changes["priority"] = {"old": old_priority, "new": priority_str}

        if assigned_to_str:
            old_assigned = ticket.get("assigned_to")
            ticket["assigned_to"] = assigned_to_str
            changes["assigned_to"] = {"old": old_assigned, "new": assigned_to_str}

        if description_str:
            ticket["description"] = description_str
            changes["description"] = "updated"

        if title_str:
            old_title = ticket.get("title")
            ticket["title"] = title_str
            changes["title"] = {"old": old_title, "new": title_str}

        if escalation_reason_str:
            old_escalation_reason = ticket.get("escalation_reason")
            ticket["escalation_reason"] = escalation_reason_str
            changes["escalation_reason"] = {
                "old": old_escalation_reason,
                "new": escalation_reason_str,
            }

        ticket["updated_at"] = timestamp

        ticket_return = ticket.copy()
        ticket_return["ticket_id"] = ticket_id_str

        return json.dumps(
            {
                "success": True,
                "ticket": ticket_return,
                "changes": changes,
                "message": f"Ticket '{ticket.get('ticket_number', ticket_id_str)}' updated successfully",
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "edit_ticket",
                "description": (
                    "Updates one or more fields of an existing support ticket. "
                    "This function modifies ticket attributes including status, priority, assignment, "
                    "description, title, and escalation reason. "
                    "Use this to reflect ticket progress through workflow stages, change priority based on impact assessment, "
                    "reassign tickets to appropriate team members, update ticket details as more information becomes available, "
                    "or record escalation reasons when elevating tickets to specialized teams."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The unique identifier of the ticket to update.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional. The new status for the ticket",
                            "enum": [
                                "open",
                                "closed",
                                "resolved",
                                "awaiting_info",
                                "in_progress",
                                "fix_proposed",
                                "pending_review",
                                "pending_security_review",
                                "archived",
                                "root_cause_identified"
                                "resolved_pending_verification",
                            ],
                        },
                        "priority": {
                            "type": "string",
                            "description": "Optional. The new priority level for the ticket",
                            "enum": ["P0", "P1", "P2", "P3"],
                        },
                        "assigned_to": {
                            "type": "string",
                            "description": "Optional. The user ID of the user to assign the ticket to.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional. The updated description for the ticket.",
                        },
                        "title": {
                            "type": "string",
                            "description": "Optional. The updated title for the ticket.",
                        },
                        "escalation_reason": {
                            "type": "string",
                            "description": "Optional. The reason for escalation",
                            "enum": [
                                "code_bug",
                                "infrastructure",
                                "security",
                                "data_corruption",
                                "access_limitation",
                            ],
                        },
                    },
                    "required": ["ticket_id"],
                },
            },
        }
