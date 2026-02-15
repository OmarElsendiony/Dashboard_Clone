import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class EscalateToExpert(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        escalated_by: str,
        escalation_reason: str,
        escalated_to: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-02 23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        def find_appropriate_expert(
            users_dict: Dict[str, Any], escalation_reason_str: str
        ) -> Optional[str]:
            expertise_mapping = {
                "code_bug": ["backend_dev", "frontend_dev"],
                "infrastructure": ["backend_dev"],
                "security": ["security_specialist"],
                "data_corruption": ["db_admin"],
                "access_limitation": ["backend_dev", "security_specialist"],
            }

            required_expertise = expertise_mapping.get(escalation_reason_str, [])

            for uid, user in users_dict.items():
                if not isinstance(user, dict):
                    continue

                user_role = str(user.get("role", "")).strip()
                user_status = str(user.get("status", "")).strip()
                user_expertise = str(user.get("technical_expertise", "")).strip()

                if (
                    user_role == "technical_engineer"
                    and user_status == "active"
                    and user_expertise in required_expertise
                ):
                    return str(uid)

            return None

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        if not ticket_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'ticket_id'"})

        if not escalated_by:
            return json.dumps({"success": False, "error": "Missing required parameter: 'escalated_by'"})

        if not escalation_reason:
            return json.dumps({"success": False, "error": "Missing required parameter: 'escalation_reason'"})

        tickets_dict = data.get("tickets", {})
        escalations_dict = data.get("escalations", {})
        users_dict = data.get("users", {})

        ticket_id_str = str(ticket_id).strip()
        escalated_by_str = str(escalated_by).strip()
        escalation_reason_str = str(escalation_reason).strip()
        escalated_to_str = str(escalated_to).strip() if escalated_to else None

        valid_escalation_reasons = [
            "code_bug",
            "infrastructure",
            "security",
            "data_corruption",
            "access_limitation",
        ]

        if escalation_reason_str not in valid_escalation_reasons:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid escalation_reason '{escalation_reason_str}'. Must be one of: {', '.join(valid_escalation_reasons)}",
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

        ticket_status = str(ticket.get("status", "")).strip()
        invalid_statuses = ["deleted", "archived", "closed"]

        if ticket_status in invalid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Cannot escalate ticket '{ticket_id_str}' with status '{ticket_status}'",
                }
            )

        if escalated_by_str not in users_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with ID '{escalated_by_str}' not found",
                }
            )

        escalator = users_dict[escalated_by_str]

        if not isinstance(escalator, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid user data structure for user ID '{escalated_by_str}'",
                }
            )

        escalator_status = escalator.get("status")
        if escalator_status != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"User '{escalated_by_str}' is not active and cannot escalate tickets",
                }
            )

        if escalated_to_str:
            if escalated_to_str not in users_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Escalation target user with ID '{escalated_to_str}' not found",
                    }
                )

            expert = users_dict[escalated_to_str]

            if not isinstance(expert, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid user data structure for expert ID '{escalated_to_str}'",
                    }
                )

            expert_role = expert.get("role")
            if expert_role != "technical_engineer":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User '{escalated_to_str}' is not a technical engineer and cannot receive escalations",
                    }
                )

            expert_status = expert.get("status")
            if expert_status != "active":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Expert '{escalated_to_str}' is not active and cannot receive escalations",
                    }
                )
        else:
            escalated_to_str = find_appropriate_expert(
                users_dict, escalation_reason_str
            )

            if not escalated_to_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"No available technical engineer found with expertise for escalation reason '{escalation_reason_str}'",
                    }
                )

        has_active_escalation = False
        for _, escalation in escalations_dict.items():
            if not isinstance(escalation, dict):
                continue
            if str(escalation.get("ticket_id", "")).strip() == ticket_id_str and str(
                escalation.get("status", "")
            ).strip() in ["pending", "assigned"]:
                has_active_escalation = True
                break

        if has_active_escalation:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Ticket '{ticket_id_str}' already has an active escalation",
                }
            )

        new_escalation_id = generate_id(escalations_dict)

        new_escalation = {
            "escalation_id": new_escalation_id,
            "ticket_id": ticket_id_str,
            "escalated_to": escalated_to_str,
            "escalated_by": escalated_by_str,
            "escalation_reason": escalation_reason_str,
            "target_domain": None,
            "status": "assigned",
            "created_at": timestamp,
            "resolved_at": None,
        }

        escalations_dict[new_escalation_id] = new_escalation

        ticket["escalation_reason"] = escalation_reason_str
        ticket["updated_at"] = timestamp

        escalation_return = new_escalation.copy()

        expert = users_dict[escalated_to_str]
        escalation_return["expert_email"] = expert.get("email")
        escalation_return["expert_name"] = (
            f"{expert.get('first_name', '')} {expert.get('last_name', '')}".strip()
        )
        escalation_return["expert_expertise"] = expert.get("technical_expertise")

        escalation_return["escalator_email"] = escalator.get("email")
        escalation_return["escalator_name"] = (
            f"{escalator.get('first_name', '')} {escalator.get('last_name', '')}".strip()
        )

        escalation_return["ticket_number"] = ticket.get("ticket_number")

        # Build success message
        message = f"Ticket '{ticket.get('ticket_number', ticket_id_str)}' escalated to expert '{expert.get('email', escalated_to_str)}' for reason '{escalation_reason_str}'"

        return json.dumps(
            {
                "success": True,
                "escalation": escalation_return,
                "message": message,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "escalate_to_expert",
                "description": (
                    "Escalates a support ticket to a subject matter expert or technical engineer when the issue "
                    "requires specialized knowledge beyond general support capabilities. "
                    "This function creates an escalation record and can automatically route to appropriate experts based on the issue type. "
                    "Use this when fixes require changes to multiple files, when issues involve code bugs requiring development expertise, "
                    "for infrastructure problems needing systems knowledge, for security concerns requiring security specialists, "
                    "when data corruption issues need database administrator intervention, or for access limitation problems. "
                    "The system can auto-assign to experts with matching technical expertise if no specific expert is specified."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The unique identifier of the ticket to escalate.",
                        },
                        "escalated_by": {
                            "type": "string",
                            "description": "The unique identifier of the user initiating the escalation.",
                        },
                        "escalation_reason": {
                            "type": "string",
                            "description": "The reason for escalation",
                            "enum": [
                                "code_bug",
                                "infrastructure",
                                "security",
                                "data_corruption",
                                "access_limitation",
                            ],
                        },
                        "escalated_to": {
                            "type": "string",
                            "description": "Optional. The unique identifier of the expert to escalate to. If not provided, system will auto-assign based on escalation reason and expert availability.",
                        },
                    },
                    "required": ["ticket_id", "escalated_by", "escalation_reason"],
                },
            },
        }
