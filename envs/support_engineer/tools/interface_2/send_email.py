import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class SendEmail(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        recipient_id: str,
        recipient_type: str,
        subject: str,
        message_body: str,
        email_type: str,
        ticket_id: str,
    ) -> str:
        timestamp = "2026-02-02 23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        if not recipient_id:
            return json.dumps(
                {
                    "success": False,
                    "error": "Missing required parameter: 'recipient_id'",
                }
            )

        if not recipient_type:
            return json.dumps(
                {
                    "success": False,
                    "error": "Missing required parameter: 'recipient_type'",
                }
            )

        if not subject:
            return json.dumps(
                {"success": False, "error": "Missing required parameter: 'subject'"}
            )

        if not message_body:
            return json.dumps(
                {
                    "success": False,
                    "error": "Missing required parameter: 'message_body'",
                }
            )

        if not email_type:
            return json.dumps(
                {"success": False, "error": "Missing required parameter: 'email_type'"}
            )

        if not ticket_id:
            return json.dumps(
                {"success": False, "error": "Missing required parameter: 'ticket_id'"}
            )

        emails_dict = data.get("emails", {})
        users_dict = data.get("users", {})
        customers_dict = data.get("customers", {})
        tickets_dict = data.get("tickets", {})

        recipient_id_str = str(recipient_id).strip()
        recipient_type_str = str(recipient_type).strip()
        subject_str = str(subject).strip()
        message_body_str = str(message_body).strip()
        email_type_str = str(email_type).strip()
        ticket_id_str = str(ticket_id).strip()

        if not subject_str:
            return json.dumps(
                {"success": False, "error": "Email subject cannot be empty"}
            )

        if not message_body_str:
            return json.dumps(
                {"success": False, "error": "Email message body cannot be empty"}
            )

        valid_recipient_types = ["user", "customer"]
        if recipient_type_str not in valid_recipient_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid recipient_type '{recipient_type_str}'. Must be one of: {', '.join(valid_recipient_types)}",
                }
            )

        valid_email_types = [
            "verification_request",
            "status_update",
            "escalation_notice",
            "resolution_notice",
        ]

        if email_type_str not in valid_email_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid email_type '{email_type_str}'. Must be one of: {', '.join(valid_email_types)}",
                }
            )

        recipient = None
        recipient_email = None

        if recipient_type_str == "user":
            if recipient_id_str not in users_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User with ID '{recipient_id_str}' not found",
                    }
                )

            recipient = users_dict[recipient_id_str]

            if not isinstance(recipient, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid user data structure for user ID '{recipient_id_str}'",
                    }
                )

            recipient_email = str(recipient.get("email", ""))

        elif recipient_type_str == "customer":
            if recipient_id_str not in customers_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Customer with ID '{recipient_id_str}' not found",
                    }
                )

            recipient = customers_dict[recipient_id_str]

            if not isinstance(recipient, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid customer data structure for customer ID '{recipient_id_str}'",
                    }
                )

            recipient_email = str(recipient.get("email", "")).strip()

        if not recipient_email:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Recipient '{recipient_id_str}' does not have an email address",
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

        if ticket_status in ["archived", "closed"]:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Cannot send email for ticket '{ticket_id_str}' with status '{ticket_status}'",
                }
            )

        if email_type_str == "verification_request":
            valid_verification_statuses = ["resolved", "resolved_pending_verification"]

            if ticket_status not in valid_verification_statuses:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Email type 'verification_request' requires ticket status 'resolved' or 'resolved_pending_verification', got '{ticket_status}'",
                    }
                )

        if email_type_str == "resolution_notice":
            if ticket_status not in [
                "resolved",
                "resolved_pending_verification",
                "closed",
            ]:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Email type 'resolution_notice' requires ticket status 'resolved', 'resolved_pending_verification', or 'closed', got '{ticket_status}'",
                    }
                )

        if email_type_str == "escalation_notice":
            escalations_dict = data.get("escalations", {})
            has_escalation = any(
                str(esc.get("ticket_id")) == ticket_id_str
                for esc in escalations_dict.values()
            )

            if not has_escalation:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Email type 'escalation_notice' requires an active escalation for ticket '{ticket_id_str}'",
                    }
                )

        new_email_id = generate_id(emails_dict)

        new_email = {
            "email_id": str(new_email_id),
            "ticket_id": str(ticket_id_str) if ticket_id_str else None,
            "template_id": None,
            "recipient_id": str(recipient_id_str) if recipient_id_str else None,
            "subject": str(subject_str) if subject_str else None,
            "message_body": str(message_body_str) if message_body_str else None,
            "email_type": str(email_type_str) if email_type_str else None,
            "status": "sent",
            "sent_at": timestamp,
            "created_at": timestamp,
        }

        emails_dict[new_email_id] = new_email

        recipient_name = ""
        if recipient_type_str == "user":
            recipient_name = f"{recipient.get('first_name', '')} {recipient.get('last_name', '')}".strip()
        elif recipient_type_str == "customer":
            recipient_name = str(recipient.get("customer_name", ""))

        email_return = {
            "email_id": str(new_email_id) if new_email_id else None,
            "ticket_id": str(ticket_id_str) if ticket_id_str else None,
            "template_id": None,
            "recipient_id": str(recipient_id_str) if recipient_id_str else None,
            "recipient_type": str(recipient_type_str) if recipient_type_str else None,
            "recipient_email": str(recipient_email) if recipient_email else None,
            "recipient_name": str(recipient_name) if recipient_name else None,
            "subject": str(subject_str) if subject_str else None,
            "message_body": str(message_body_str) if message_body_str else None,
            "email_type": str(email_type_str) if email_type_str else None,
            "status": "sent",
            "sent_at": timestamp,
            "created_at": timestamp,
            "ticket_number": str(tickets_dict[ticket_id_str].get("ticket_number", "")),
        }

        ticket_number = str(
            tickets_dict.get(ticket_id_str, {}).get("ticket_number", ticket_id_str)
        )
        message = f"Email sent successfully to {recipient_email} regarding ticket '{ticket_number}'"

        return json.dumps(
            {
                "success": True,
                "email": email_return,
                "message": message,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "send_email",
                "description": "Sends an email notification to a recipient (customer or internal user) regarding ticket updates, resolutions, or other support communications. "
                "Use this to notify customers of ticket status changes, request verification of fixes, "
                "send escalation notices to stakeholders, or deliver resolution confirmations. "
                "Supports different email types including verification requests, status updates, escalation notices, and resolution notices.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipient_id": {
                            "type": "string",
                            "description": "The unique identifier of the recipient (user ID or customer ID).",
                        },
                        "recipient_type": {
                            "type": "string",
                            "description": "The type of recipient (required to determine where to look up the recipient)",
                            "enum": ["user", "customer"],
                        },
                        "subject": {
                            "type": "string",
                            "description": "The subject line of the email.",
                        },
                        "message_body": {
                            "type": "string",
                            "description": "The content/body of the email message.",
                        },
                        "email_type": {
                            "type": "string",
                            "description": "The type of email being sent",
                            "enum": [
                                "verification_request",
                                "status_update",
                                "escalation_notice",
                                "resolution_notice",
                            ],
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "The unique identifier of the ticket this email relates to.",
                        },
                    },
                    "required": [
                        "recipient_id",
                        "recipient_type",
                        "subject",
                        "message_body",
                        "email_type",
                        "ticket_id",
                    ],
                },
            },
        }
