import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class CreateEscalationRecord(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        target_domain: str,
        escalation_reason: str,
        escalated_by: str,
        escalated_to: str,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        tickets = data.get("tickets", {})
        escalations = data.get("escalations", {})
        users = data.get("users", {})

        if not ticket_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'ticket_id' is required."})

        if not target_domain:
            return json.dumps({"success": False, "error": "Missing Argument: 'target_domain' is required."})

        if not escalation_reason:
            return json.dumps({"success": False, "error": "Missing Argument: 'escalation_reason' is required."})

        if not escalated_by:
            return json.dumps({"success": False, "error": "Missing Argument: 'escalated_by' is required."})

        if not escalated_to:
             return json.dumps({
                "success": False,
                "error": "Missing Argument: 'escalated_to' (User ID) is required to route this escalation."
            })

        ticket_id = str(ticket_id).strip()
        target_domain = str(target_domain).strip()
        escalation_reason = str(escalation_reason).strip()
        escalated_by = str(escalated_by).strip()
        escalated_to = str(escalated_to).strip()

        if ticket_id not in tickets:
            return json.dumps({"success": False, "error": f"Not Found Error: Ticket ID '{ticket_id}' not found."})

        valid_domains = ["Legal", "Security", "SecOps", "Billing"]
        if target_domain not in valid_domains:
             return json.dumps({
                "success": False,
                "error": f"Invalid Argument: target_domain must be one of {valid_domains}."
            })

        valid_reasons = [
            "code_bug", "infrastructure", "security",
            "data_corruption", "access_limitation",
            "Keyword_Detection", "SLA_Breach"
        ]
        if escalation_reason not in valid_reasons:
             return json.dumps({
                "success": False,
                "error": f"Invalid Argument: escalation_reason must be one of {valid_reasons}."
            })

        if escalated_by not in users:
            return json.dumps({"success": False, "error": f"Auth Error: User ID '{escalated_by}' (escalated_by) not found."})

        if escalated_to not in users:
             return json.dumps({
                "success": False,
                "error": f"Target Error: User ID '{escalated_to}' (escalated_to) not found."})

        for esc in escalations.values():
            if not isinstance(esc, dict):
                continue
            if (
                str(esc.get("ticket_id")) == ticket_id and
                str(esc.get("target_domain")) == target_domain and
                str(esc.get("escalation_reason")) == escalation_reason and
                str(esc.get("escalated_by")) == escalated_by and
                str(esc.get("escalated_to")) == escalated_to
            ):
                return json.dumps({
                    "success": False,
                    "error": "Duplicate Escalation Detected",
                    "message": f"Idempotency violation: An identical escalation record for ticket '{ticket_id}' to domain '{target_domain}' by user '{escalated_by}' already exists. Infinite writes are blocked."
                })

        max_id = 0
        for k in escalations.keys():
            try:
                num = int(str(k))
                if num > max_id:
                    max_id = num
            except ValueError:
                continue

        new_id = str(max_id + 1)
        timestamp = "2026-02-02 23:59:00"

        new_escalation = {
            "escalation_id": new_id,
            "ticket_id": ticket_id,
            "escalated_to": escalated_to,
            "escalated_by": escalated_by,
            "escalation_reason": escalation_reason,
            "target_domain": target_domain,
            "status": "pending",
            "created_at": timestamp
        }

        escalations[new_id] = new_escalation

        return json.dumps({
            "success": True,
            "escalation": new_escalation,
            "message": f"Escalation Record #{new_id} created successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_escalation_record",
                "description": (
                    "Generates a formal record in the escalations table.\n"
                    "Purpose: Triggers the official handoff process when an issue requires expertise beyond Support (e.g., Legal, Security). Includes an idempotency check to prevent duplicate escalation records.\n"
                    "When to use: When a ticket cannot be resolved by the support team due to access limits, legal implications, or security risks.\n"
                    "Returns: The created escalation record. Fails explicitly if an identical escalation record already exists to prevent infinite writes."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "REQUIRED. The ID of the Support Ticket being escalated."
                        },
                        "target_domain": {
                            "type": "string",
                            "enum": ["Legal", "Security", "SecOps", "Billing"],
                            "description": "REQUIRED. The specific department receiving the handoff."
                        },
                        "escalation_reason": {
                            "type": "string",
                            "enum": ["code_bug", "infrastructure", "security", "data_corruption", "access_limitation", "Keyword_Detection", "SLA_Breach"],
                            "description": "REQUIRED. The technical justification for the escalation."
                        },
                        "escalated_by": {
                            "type": "string",
                            "description": "REQUIRED. The User ID of the Support Engineer performing the action."
                        },
                        "escalated_to": {
                            "type": "string",
                            "description": "REQUIRED. The User ID of the recipient or the specific queue owner ID."
                        }
                    },
                    "required": ["ticket_id", "target_domain", "escalation_reason", "escalated_by", "escalated_to"]
                }
            }
        }
