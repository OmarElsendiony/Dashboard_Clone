import json
from typing import Dict, Optional
from tau_bench.envs.tool import Tool


class GetTicketsList(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, object],
        status: str,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for tickets"}
            )

        if not status:
            return json.dumps({"success": False, "error": "status is required"})

        tickets = data.get("tickets", {})
        results = []

        valid_priorities = ["P0", "P1", "P2", "P3", "P4"]
        if priority and priority not in valid_priorities:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid priority '{priority}'. Must be one of: {', '.join(valid_priorities)}",
                }
            )
        
        valid_status = [
                        "archived",
                        "awaiting_info",
                        "closed",
                        "escalated",
                        "fix_in_progress",
                        "fix_proposed",
                        "fix_rejected",
                        "in_progress",
                        "open",
                        "pending",
                        "pending_review",
                        "pending_security_review",
                        "ready_for_investigation",
                        "resolved",
                        "root_cause_identified",
                            ]
        if status and status not in valid_status:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_status)}",
                }
            )

        for ticket_id, ticket_data in tickets.items():
            if ticket_data.get("status") != status:
                continue
            if priority and ticket_data.get("priority") != priority:
                continue
            if assigned_to and str(ticket_data.get("assigned_to")) != str(assigned_to):
                continue

            results.append({**ticket_data, "ticket_id": ticket_id})

        results.sort(key=lambda x: x.get("created_at", ""))

        return json.dumps(
            {
                "success": True,
                "count": len(results),
                "tickets": results,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, object]:
        return {
            "type": "function",
            "function": {
                "name": "get_tickets_list",
                "description": "Get a list of tickets filtered by their status. Perfect for finding existing tickets to check for duplicates or reviewing tickets in a specific state. You can also filter by priority level or who the ticket is assigned to. Results are sorted from oldest to newest for easy review.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Filter by ticket status",
                            "enum": [
                                "archived",
                                "awaiting_info",
                                "closed",
                                "escalated",
                                "fix_in_progress",
                                "fix_proposed",
                                "fix_rejected",
                                "in_progress",
                                "open",
                                "pending",
                                "pending_review",
                                "pending_security_review",
                                "ready_for_investigation",
                                "resolved",
                                "root_cause_identified",
                            ],
                        },
                        "priority": {
                            "type": "string",
                            "description": "Filter by ticket priority.",
                            "enum": ["P0", "P1", "P2", "P3", "P4"],
                        },
                        "assigned_to": {
                            "type": "string",
                            "description": "Filter by user ID of the assigned agent",
                        },
                    },
                    "required": ["status"],
                },
            },
        }
