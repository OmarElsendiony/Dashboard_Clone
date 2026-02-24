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
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return json.dumps({
                    "success": bool(False),
                    "error": str("Wrong data format"),
                })
        if not isinstance(data, dict):
            return json.dumps({
                "success": bool(False),
                "error": str("Wrong data format"),
            })

        customer_id_str = str(customer_id).strip() if customer_id is not None else ""
        if not customer_id_str:
            return json.dumps({
                "success": bool(False),
                "error": str("customer_id is required"),
            })

        if title is None:
            return json.dumps({
                "success": bool(False),
                "error": str("title is required"),
            })
        title = str(title).strip()
        if not title:
            return json.dumps({
                "success": bool(False),
                "error": str("title is required"),
            })

        if description is None:
            return json.dumps({
                "success": bool(False),
                "error": str("description is required"),
            })
        description = str(description).strip()
        if not description:
            return json.dumps({
                "success": bool(False),
                "error": str("description is required"),
            })

        status = str(status).strip() if status is not None and str(status).strip() else str("open")
        if priority is not None:
            valid_priorities = ["P1", "P2", "P3"]
            if priority not in valid_priorities:
                return json.dumps({
                    "success": bool(False),
                    "error": str(
                        f"Invalid priority '{priority}'. Valid values: P1, P2, P3"
                    ),
                })

        valid_statuses = ["open", "closed", "pending", "in_progress"]
        if status not in valid_statuses:
            return json.dumps({
                "success": bool(False),
                "error": str(
                    f"Invalid status '{status}'. Valid values: {', '.join(valid_statuses)}"
                ),
            })

        customers = data.get("customers", {})
        tickets = data.get("tickets", {})

        if customer_id_str not in customers:
            return json.dumps({
                "success": bool(False),
                "error": str(f"Customer with id '{customer_id_str}' not found"),
            })

        customer = customers[customer_id_str]
        if customer.get("status") == "inactive":
            return json.dumps({
                "success": bool(False),
                "error": str(
                    f"Inactive customers cannot create tickets. Customer '{customer_id_str}' has status 'inactive'."
                ),
            })

        if tickets:
            max_id = max(int(k) for k in tickets.keys())
            new_ticket_id = str(max_id + 1)
        else:
            new_ticket_id = str("1")

        existing_ticket_numbers = [
            ticket.get("ticket_number", "")
            for ticket in tickets.values()
            if ticket.get("ticket_number", "").startswith("TKT-")
        ]

        if existing_ticket_numbers:
            max_ticket_number = max(
                int(tn.split("-")[1]) for tn in existing_ticket_numbers
            )
            new_ticket_number = str(f"TKT-{str(max_ticket_number + 1).zfill(6)}")
        else:
            new_ticket_number = str("TKT-000001")

        static_timestamp = str("2026-02-02 23:59:00")

        new_ticket = {
            "ticket_id": str(new_ticket_id),
            "ticket_number": str(new_ticket_number),
            "customer_id": str(customer_id_str),
            "assigned_to": None,
            "title": str(title),
            "description": str(description),
            "priority": str(priority) if priority is not None else None,
            "status": str(status),
            "created_at": str(static_timestamp),
            "updated_at": str(static_timestamp),
        }

        tickets[new_ticket_id] = new_ticket

        ticket_response = {
            "ticket_id": str(new_ticket["ticket_id"]),
            "ticket_number": str(new_ticket["ticket_number"]),
            "customer_id": str(new_ticket["customer_id"]),
            "assigned_to": new_ticket["assigned_to"],
            "title": str(new_ticket["title"]),
            "description": str(new_ticket["description"]),
            "priority": str(new_ticket["priority"]) if new_ticket["priority"] is not None else None,
            "status": str(new_ticket["status"]),
            "created_at": str(new_ticket["created_at"]),
            "updated_at": str(new_ticket["updated_at"]),
        }

        return json.dumps({
            "success": bool(True),
            "ticket": ticket_response,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_new_ticket",
                "description": "Creates a new support ticket for a customer issue or problem report.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "Customer identifier who reported the issue.",
                        },
                        "title": {
                            "type": "string",
                            "description": "Brief title summarizing the issue.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed description of the issue.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Initial ticket status. Defaults to open if omitted.",
                            "enum": ["open", "closed", "pending", "in_progress"],
                        },
                        "priority": {
                            "type": "string",
                            "description": "Ticket priority level (P1, P2, or P3).",
                            "enum": ["P1", "P2", "P3"],
                        },
                    },
                    "required": ["customer_id", "title", "description"],
                },
            },
        }
