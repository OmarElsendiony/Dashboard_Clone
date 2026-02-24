import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class SendTicketEmailReply(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        ticket_id: str,
        recipient_id: str,
        subject: str,
        message_body: str,
        email_type: str = "status_update",
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

        if not ticket_id:
            return json.dumps({
                "success": bool(False),
                "error": str("ticket_id is required"),
            })

        if not recipient_id:
            return json.dumps({
                "success": bool(False),
                "error": str("recipient_id is required"),
            })

        if not subject:
            return json.dumps({
                "success": bool(False),
                "error": str("subject is required"),
            })

        if not message_body:
            return json.dumps({
                "success": bool(False),
                "error": str("message_body is required"),
            })

        valid_email_types = [
            "verification_request",
            "status_update",
            "resolution_notice",
        ]

        if email_type not in valid_email_types:
            return json.dumps({
                "success": bool(False),
                "error": str(f"Invalid email_type '{email_type}'. Valid values: {', '.join(valid_email_types)}"),
            })

        tickets = data.get("tickets", {})
        customers = data.get("customers", {})
        emails = data.get("emails", {})

        if str(ticket_id) not in tickets:
            return json.dumps({
                "success": bool(False),
                "error": str(f"Ticket with id '{ticket_id}' not found"),
            })

        if str(recipient_id) not in customers:
            return json.dumps({
                "success": bool(False),
                "error": str(f"Customer with id '{recipient_id}' not found"),
            })

        customer = customers[str(recipient_id)]
        if customer.get("status") != "active":
            return json.dumps({
                "success": bool(False),
                "error": str(f"Customer with id '{recipient_id}' is not active. Current status: {customer.get('status')}. Cannot send email to inactive customers"),
            })

        if emails:
            max_id = max(int(k) for k in emails.keys())
            new_email_id = str(max_id + 1)
        else:
            new_email_id = str("1")

        static_timestamp = str("2026-02-02 23:59:00")

        new_email = {
            "email_id": str(new_email_id),
            "ticket_id": str(ticket_id),
            "template_id": None,
            "recipient_id": str(recipient_id),
            "subject": str(subject),
            "message_body": str(message_body),
            "email_type": str(email_type),
            "status": str("sent"),
            "sent_at": str(static_timestamp),
            "created_at": str(static_timestamp),
        }

        emails[new_email_id] = new_email

        email_response = {
            "email_id": str(new_email_id),
            "ticket_id": str(ticket_id),
            "recipient_id": str(recipient_id),
            "subject": str(subject),
            "message_body": str(message_body),
            "email_type": str(email_type),
            "status": str("sent"),
            "sent_at": str(static_timestamp),
        }
        return json.dumps({
            "success": bool(True),
            "email": email_response,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "send_ticket_email_reply",
                "description": "Send an email reply to a customer about a ticket.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "Ticket identifier the email relates to",
                        },
                        "recipient_id": {
                            "type": "string",
                            "description": "Customer identifier receiving the email",
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject line",
                        },
                        "message_body": {
                            "type": "string",
                            "description": "Email message content",
                        },
                        "email_type": {
                            "type": "string",
                            "description": "Type of email being sent. Defaults to status_update if omitted.",
                            "enum": ["verification_request", "status_update", "resolution_notice"],
                        },
                    },
                    "required": ["ticket_id", "recipient_id", "subject", "message_body"],
                },
            },
        }
