import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CloseTicket(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: Optional[str] = None,
        ticket_number: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not any([ticket_id, ticket_number]):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one parameter must be provided: ticket_id or ticket_number",
                }
            )

        tickets = data.get("tickets", {})

        target_ticket = None

        if ticket_id:
            if str(ticket_id) in tickets:
                target_ticket = tickets[str(ticket_id)]
            else:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Ticket with id '{ticket_id}' not found",
                    }
                )
        elif ticket_number:
            for ticket in tickets.values():
                if ticket.get("ticket_number") == ticket_number:
                    target_ticket = ticket
                    break
            if not target_ticket:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Ticket with number '{ticket_number}' not found",
                    }
                )

        current_status = target_ticket.get("status")
        if current_status in ["closed"]:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Ticket is already {current_status}. Cannot close a ticket that is already closed",
                }
            )

        customers = data.get("customers", {})
        customer_id = target_ticket.get("customer_id")
        if customer_id is None or str(customer_id) not in customers:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Cannot close ticket: customer for ticket '{target_ticket.get('ticket_id')}' not found.",
                }
            )
        customer = customers[str(customer_id)]
        if customer.get("status") != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"Cannot close ticket: customer '{customer_id}' does not have active status (current: {customer.get('status') or 'unknown'}). Verify active customer before closing.",
                }
            )

        pull_requests = data.get("pull_requests", {})
        tid = str(target_ticket.get("ticket_id"))
        merged_pr_for_ticket = any(
            str(pr.get("linked_ticket_id")) == tid and pr.get("status") == "merged"
            for pr in pull_requests.values()
        )
        if not merged_pr_for_ticket:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Cannot close ticket: no merged PR linked to ticket '{tid}'. It is required to have a merged PR before closing.",
                }
            )

        static_timestamp = "2026-02-02 23:59:00"

        target_ticket["status"] = "closed"
        target_ticket["closed_at"] = static_timestamp
        target_ticket["updated_at"] = static_timestamp

        _EXCLUDE_KEYS = {
            "ingestion_channel",
            "kb_article_link",
            "incident_timestamp",
            "escalation_reason",
            "created_at",
        }
        _EXCLUDE_PREFIXES = ("incident_", "escalation_", "space_")
        ticket_response = {
            k: v
            for k, v in target_ticket.items()
            if k not in _EXCLUDE_KEYS and not k.startswith(_EXCLUDE_PREFIXES)
        }
        return json.dumps({"success": True, "ticket": ticket_response})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "close_ticket",
                "description": "Close a support ticket.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket identifier",
                        },
                        "ticket_number": {
                            "type": "string",
                            "description": "Ticket number",
                        },
                    },
                    "required": [],
                    "oneOf": [
                        {"required": ["ticket_id"]},
                        {"required": ["ticket_number"]},
                    ],
                },
            },
        }
