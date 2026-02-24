import json
from typing import Dict, Optional, Any
from tau_bench.envs.tool import Tool


class ModifyTicket(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_number: str,
        status: Optional[str] = None,
        escalation_reason: Optional[str] = None,
    ) -> str:
        tickets = data.get("tickets", {})
        timestamp = "2026-02-02 23:59:00"

        if not ticket_number:
            return json.dumps({"success": False, "error": "ticket_number is required"})

        if not status and not escalation_reason:
            return json.dumps({
                "success": False,
                "error": "At least one of status or escalation_reason must be provided"
            })

        valid_statuses = (
            "open",
            "awaiting_info",
            "ready_for_investigation",
            "root_cause_identified",
            "in_progress",
            "escalated",
            "resolved",
            "fix_rejected",
            "closed",
        )

        if status and status not in valid_statuses:
            return json.dumps({
                "success": False,
                "error": (
                    f"Invalid status '{status}'. Valid values: "
                    "open, awaiting_info, ready_for_investigation, "
                    "root_cause_identified, in_progress, "
                    "escalated, resolved, fix_rejected, closed."
                )
            })

        if status == "escalated" and not escalation_reason:
            return json.dumps({
                "success": False,
                "error": "escalation_reason must be provided when status is 'escalated'"
            })

        valid_escalation_reasons = ["code_bug", "infrastructure", "security", "data_corruption", "access_limitation"]
        if escalation_reason and escalation_reason not in valid_escalation_reasons:
            return json.dumps({
                "success": False,
                "error": (
                    f"Invalid escalation_reason '{escalation_reason}'. Valid values: "
                    "code_bug, infrastructure, security, data_corruption, access_limitation."
                )
            })

        tickets = data.get("tickets", {})

        ticket_details = None

        for t_details in tickets.values():
            if t_details.get("ticket_number") == str(ticket_number):
                ticket_details = t_details
                break

        if not ticket_details:
            return json.dumps({
                "success": False,
                "error": f"Ticket with number '{ticket_number}' not found"
            })

        if status:
            ticket_details["status"] = str(status)

        if escalation_reason:
            ticket_details["escalation_reason"] = str(escalation_reason)

        ticket_details["updated_at"] = timestamp

        return json.dumps({
            "success": True,
            "ticket": {
                "ticket_id": str(ticket_details.get("ticket_id")),
                "ticket_number": str(ticket_details.get("ticket_number")),
                "title": str(ticket_details.get("title")),
                "status": status if status else str(ticket_details.get("status")),
                "escalation_reason": escalation_reason if escalation_reason else ticket_details.get("escalation_reason"),
                "updated_at": str(ticket_details.get("updated_at")),
            },
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "modify_ticket",
                "description": "Modifies the status or escalation reason of a ticket. This should be used when you want to update the status of a ticket or provide an escalation reason.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_number": {
                            "type": "string",
                            "description": "The ticket number to modify",
                        },
                        "status": {
                            "type": "string",
                            "description": "The new status for the ticket",
                            "enum": [
                                "open",
                                "awaiting_info",
                                "ready_for_investigation",
                                "root_cause_identified",
                                "in_progress",
                                "escalated",
                                "resolved",
                                "fix_rejected",
                                "closed",
                            ],
                        },
                        "escalation_reason": {
                            "type": "string",
                            "description": "The reason for escalation when status is set to 'escalated'",
                            "enum": ["code_bug", "infrastructure", "security", "data_corruption", "access_limitation"]
                        }
                    },
                    "required": ["ticket_number"],
                    "anyOf": [
                        {"required": ["status"]},
                        {"required": ["escalation_reason"]}
                    ]
                },
            },
        }
