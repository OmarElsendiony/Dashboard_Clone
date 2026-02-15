import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class AddNewTicket(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        customer_id: str,
        title: str,
        description: str,
        status: str = "open",
        priority: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not customer_id:
            return json.dumps(
                {"success": False, "error": "customer_id is required"}
            )

        if not title:
            return json.dumps({"success": False, "error": "title is required"})

        if not description:
            return json.dumps(
                {"success": False, "error": "description is required"}
            )

        if priority is not None:
            valid_priorities = ["P1", "P2", "P3"]
            if priority not in valid_priorities:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid priority '{priority}'. Valid values: P1, P2, P3",
                    }
                )

        valid_statuses = [
            "open", "closed", "pending", "in_progress"
        ]
        if status not in valid_statuses:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status '{status}'. Valid values: {', '.join(valid_statuses)}",
                }
            )

        customers = data.get("customers", {})
        tickets = data.get("tickets", {})

        if str(customer_id) not in customers:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Customer with id '{customer_id}' not found",
                }
            )

        customer = customers[str(customer_id)]
        if customer.get("status") == "inactive":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Inactive customers cannot create tickets. Customer '{customer_id}' has status 'inactive'.",
                }
            )

        if tickets:
            max_id = max(int(k) for k in tickets.keys())
            new_ticket_id = str(max_id + 1)
        else:
            new_ticket_id = "1"

        existing_ticket_numbers = [
            ticket.get("ticket_number", "")
            for ticket in tickets.values()
            if ticket.get("ticket_number", "").startswith("TKT-")
        ]

        if existing_ticket_numbers:
            max_ticket_number = max(
                int(tn.split("-")[1]) for tn in existing_ticket_numbers
            )
            new_ticket_number = f"TKT-{str(max_ticket_number + 1).zfill(6)}"
        else:
            new_ticket_number = "TKT-000001"

        static_timestamp = "2026-02-02 23:59:00"

        new_ticket = {
            "ticket_id": str(new_ticket_id),
            "ticket_number": new_ticket_number,
            "customer_id": str(customer_id),
            "assigned_to": None,
            "title": title,
            "description": description,
            "priority": priority,
            "status": status,
            "created_at": static_timestamp,
            "updated_at": static_timestamp,
        }

        tickets[new_ticket_id] = new_ticket

        _EXCLUDE_KEYS = {
            "ingestion_channel",
            "kb_article_link",
            "incident_timestamp",
            "escalation_reason"
        }
        _EXCLUDE_PREFIXES = ("incident_", "escalation_", "space_")
        ticket_response = {
            k: v
            for k, v in new_ticket.items()
            if k not in _EXCLUDE_KEYS and not k.startswith(_EXCLUDE_PREFIXES)
        }
        return json.dumps({"success": True, "ticket": ticket_response})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_new_ticket",
                "description": "Create a new support ticket for a customer issue or problem report.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "Customer identifier who reported the issue",
                        },
                        "title": {
                            "type": "string",
                            "description": "Brief title summarizing the issue",
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed description of the issue",
                        },
                        "status": {
                            "type": "string",
                            "description": "Initial ticket status",
                            "enum": ["open", "closed", "pending", "in_progress"]
                        },
                        "priority": {
                            "type": "string",
                            "description": "Ticket priority level",
                        },
                    },
                    "required": ["customer_id", "title", "description"],
                },
            },
        }
