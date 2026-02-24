import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class AssignSeverityLevel(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        severity: str,
    ) -> str:
        timestamp = "2026-02-02 23:59:00"

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        tickets_dict = data.get("tickets", {})

        if not ticket_id or not severity:
            return json.dumps(
                {
                    "success": False,
                    "error": "Both 'ticket_id' and 'severity' parameters are required and cannot be empty",
                }
            )

        ticket_id_str = str(ticket_id).strip()
        severity_str = str(severity).strip()

        if not severity_str:
            return json.dumps(
                {"success": False, "error": "Severity level cannot be empty"}
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

        valid_severities = ["P0", "P1", "P2", "P3"]

        if severity_str not in valid_severities:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid severity level '{severity_str}'. Must be one of: {', '.join(valid_severities)}",
                }
            )

        ticket_status = str(ticket.get("status", "")).strip()
        invalid_statuses = ["deleted", "archived"]

        if ticket_status in invalid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Cannot assign severity to ticket '{ticket_id_str}' with status '{ticket_status}'",
                }
            )

        old_priority = ticket.get("priority")

        ticket["priority"] = str(severity_str) if severity_str else None
        ticket["updated_at"] = timestamp

        ticket_return = ticket.copy()
        ticket_return["ticket_id"] = str(ticket_id_str) if ticket_id_str else None

        severity_descriptions = {
            "P0": "Critical",
            "P1": "High",
            "P2": "Medium",
            "P3": "Low",
        }

        severity_description = severity_descriptions.get(severity_str, severity_str)

        message = f"Severity level '{severity_str}' ({severity_description}) assigned to ticket '{ticket.get('ticket_number', ticket_id_str)}'"
        if old_priority and old_priority != severity_str:
            old_description = severity_descriptions.get(old_priority, old_priority)
            message += f" (changed from '{old_priority}' ({old_description}))"

        return json.dumps(
            {
                "success": True,
                "ticket": ticket_return,
                "new_priority": severity_str,
                "severity_description": severity_description,
                "message": message,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "assign_severity_level",
                "description": (
                    "Assigns a severity level (priority) to a support ticket based on impact assessment. "
                    "This function categorizes tickets into priority levels from P0 (Critical) to P3 (Low), "
                    "which determines response time targets and escalation requirements. "
                    "Use this after evaluating ticket impact to classify complete service outages as P0 (Critical), "
                    "service degradation affecting multiple customers as P1 (High), "
                    "functionality impairment affecting single customer as P2 (Medium), "
                    "or cosmetic issues and feature requests as P3 (Low). "
                    "The assigned severity drives SLA response targets and routing decisions."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The unique identifier of the ticket to assign severity to.",
                        },
                        "severity": {
                            "type": "string",
                            "description": "The severity level to assign",
                            "enum": ["P0", "P1", "P2", "P3"],
                        },
                    },
                    "required": ["ticket_id", "severity"],
                },
            },
        }
