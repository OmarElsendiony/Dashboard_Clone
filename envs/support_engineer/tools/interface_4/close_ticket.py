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

        has_id = ticket_id is not None and (not isinstance(ticket_id, str) or ticket_id.strip())
        has_number = ticket_number is not None and (not isinstance(ticket_number, str) or ticket_number.strip())
        if has_id and has_number:
            return json.dumps({
                "success": bool(False),
                "error": str("Exactly one of ticket_id or ticket_number must be provided, not both."),
            })
        if not has_id and not has_number:
            return json.dumps({
                "success": bool(False),
                "error": str("At least one of ticket_id or ticket_number is required."),
            })

        tickets = data.get("tickets", {})

        target_ticket = None

        if has_id:
            ticket_id = str(ticket_id).strip()
            if ticket_id in tickets:
                target_ticket = tickets[ticket_id]
            else:
                return json.dumps({
                    "success": bool(False),
                    "error": str(f"Ticket with id '{ticket_id}' not found"),
                })
        else:
            ticket_number = str(ticket_number).strip()
            for ticket in tickets.values():
                if ticket.get("ticket_number") == ticket_number:
                    target_ticket = ticket
                    break
            if not target_ticket:
                return json.dumps({
                    "success": bool(False),
                    "error": str(f"Ticket with number '{ticket_number}' not found"),
                })

        current_status = target_ticket.get("status")
        if current_status == "closed":
            return json.dumps({
                "success": bool(False),
                "error": str(f"Ticket is already closed. Cannot close a ticket that is already closed"),
            })

        customers = data.get("customers", {})
        customer_id = target_ticket.get("customer_id")
        if customer_id is None or str(customer_id) not in customers:
            return json.dumps({
                "success": bool(False),
                "error": str(f"Cannot close ticket: customer for ticket '{target_ticket.get('ticket_id')}' not found."),
            })
        customer = customers[str(customer_id)]
        if customer.get("status") != "active":
            return json.dumps({
                "success": bool(False),
                "error": str(f"Cannot close ticket: customer '{customer_id}' does not have active status (current: {customer.get('status') or 'unknown'}). Verify active customer before closing."),
            })

        pull_requests = data.get("pull_requests", {})
        tid = str(target_ticket.get("ticket_id"))
        merged_pr_for_ticket = any(
            str(pr.get("linked_ticket_id")) == tid and pr.get("status") == "merged"
            for pr in pull_requests.values()
        )
        if not merged_pr_for_ticket:
            return json.dumps({
                "success": bool(False),
                "error": str(f"Cannot close ticket: no merged PR linked to ticket '{tid}'. It is required to have a merged PR before closing."),
            })

        static_timestamp = "2026-02-02 23:59:00"

        target_ticket["status"] = "closed"
        target_ticket["closed_at"] = static_timestamp
        target_ticket["updated_at"] = static_timestamp

        exclude_keys = {
            "ingestion_channel",
            "kb_article_link",
            "incident_timestamp",
            "escalation_reason",
            "created_at",
        }
        exclude_prefixes = ("incident_", "escalation_", "space_")
        ticket_response = {}
        for k, v in target_ticket.items():
            if k not in exclude_keys and not k.startswith(exclude_prefixes):
                ticket_response[k] = str(v) if v is not None else None

        return json.dumps({
            "success": bool(True),
            "ticket": ticket_response,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "close_ticket",
                "description": "Closes a support ticket.",
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
