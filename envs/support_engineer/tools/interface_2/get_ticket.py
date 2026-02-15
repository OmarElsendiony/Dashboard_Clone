import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetTicket(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_number: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        if not ticket_number:
            return json.dumps({"success": False, "error": "Missing required parameter: 'ticket_number'"})

        tickets_dict = data.get("tickets", {})
        search_number = str(ticket_number).strip()

        target_ticket = None
        target_ticket_id = None

        # Search for ticket by ticket_number (value) as we shouldn't rely on IDs (Common Error #8)
        for t_id, t_data in tickets_dict.items():
            if str(t_data.get("ticket_number", "")) == search_number:
                target_ticket = t_data
                target_ticket_id = t_id
                break

        if not target_ticket:
             return json.dumps({
                "success": False,
                "error": f"Ticket with number '{search_number}' not found"
            })

        # Prepare response object ensuring correct datatypes based on schema
        response = {
            "ticket_id": str(target_ticket_id),
            "ticket_number": str(target_ticket.get("ticket_number", "")),
            "customer_id": str(target_ticket.get("customer_id", "")),
            "assigned_to": str(target_ticket.get("assigned_to", "")) if target_ticket.get("assigned_to") else None,
            "title": str(target_ticket.get("title", "")),
            "description": str(target_ticket.get("description", "")),
            "priority": str(target_ticket.get("priority", "P3")),
            "status": str(target_ticket.get("status", "open")),
            "kb_article_link": str(target_ticket.get("kb_article_link", "")) if target_ticket.get("kb_article_link") else None,
            "incident_timestamp": str(target_ticket.get("incident_timestamp", "")) if target_ticket.get("incident_timestamp") else None,
            "created_at": str(target_ticket.get("created_at", "")),
            "updated_at": str(target_ticket.get("updated_at", "")),
            "resolved_at": str(target_ticket.get("resolved_at", "")) if target_ticket.get("resolved_at") else None,
            "closed_at": str(target_ticket.get("closed_at", "")) if target_ticket.get("closed_at") else None,
        }

        return json.dumps({
            "success": True,
            "ticket": response
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_ticket",
                "description": (
                    "Retrieves complete ticket details including status, priority, customer information, and content. "
                    "This function provides the foundation for all ticket processing workflows. "
                    "Use this as the first step in ticket intake to validate existence and state, "
                    "before severity assessment to understand the issue context, "
                    "when checking actionability to evaluate completeness, "
                    "or prior to any status updates to confirm current workflow position."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_number": {
                            "type": "string",
                            "description": "The unique public identifier (e.g., 'T-1001') of the ticket to retrieve."
                        }
                    },
                    "required": ["ticket_number"]
                }
            }
        }
