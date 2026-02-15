import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class SendEmail(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        recipient_id: str,
        subject: str,
        message_body: str,
        email_type: str,
        ticket_id: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-02 23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        if not recipient_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'recipient_id'"})

        if not subject:
            return json.dumps({"success": False, "error": "Missing required parameter: 'subject'"})

        if not message_body:
            return json.dumps({"success": False, "error": "Missing required parameter: 'message_body'"})

        if not email_type:
            return json.dumps({"success": False, "error": "Missing required parameter: 'email_type'"})

        emails_dict = data.get("emails", {})
        users_dict = data.get("users", {})
        customers_dict = data.get("customers", {})
        tickets_dict = data.get("tickets", {})

        recipient_id_str = str(recipient_id).strip()
        subject_str = str(subject).strip()
        message_body_str = str(message_body).strip()
        email_type_str = str(email_type).strip()
        ticket_id_str = str(ticket_id).strip() if ticket_id else None

        if not subject_str:
            return json.dumps({
                "success": False,
                "error": "Email subject cannot be empty"
            })

        if not message_body_str:
            return json.dumps({
                "success": False,
                "error": "Email message body cannot be empty"
            })

        valid_email_types = [
            'verification_request',
            'status_update',
            'escalation_notice',
            'resolution_notice'
        ]

        if email_type_str not in valid_email_types:
            return json.dumps({
                "success": False,
                "error": f"Invalid email_type '{email_type_str}'. Must be one of: {', '.join(valid_email_types)}"
            })

        # Check if recipient exists (could be user or customer)
        recipient = None
        recipient_email = None
        recipient_type = None

        # Try to find recipient in users first
        if recipient_id_str in users_dict:
            recipient = users_dict[recipient_id_str]
            recipient_type = "user"

            if not isinstance(recipient, dict):
                return json.dumps({
                    "success": False,
                    "error": f"Invalid user data structure for recipient ID '{recipient_id_str}'"
                })

            recipient_email = recipient.get("email")

        # Try to find recipient in customers
        elif recipient_id_str in customers_dict:
            recipient = customers_dict[recipient_id_str]
            recipient_type = "customer"

            if not isinstance(recipient, dict):
                return json.dumps({
                    "success": False,
                    "error": f"Invalid customer data structure for recipient ID '{recipient_id_str}'"
                })

            recipient_email = recipient.get("email")

        else:
            return json.dumps({
                "success": False,
                "error": f"Recipient with ID '{recipient_id_str}' not found in users or customers"
            })

        # Validate recipient has an email address
        if not recipient_email:
            return json.dumps({
                "success": False,
                "error": f"Recipient '{recipient_id_str}' does not have an email address"
            })

        if ticket_id_str:
            if ticket_id_str not in tickets_dict:
                return json.dumps({
                    "success": False,
                    "error": f"Ticket with ID '{ticket_id_str}' not found"
                })

            ticket = tickets_dict[ticket_id_str]

            if not isinstance(ticket, dict):
                return json.dumps({
                    "success": False,
                    "error": f"Invalid ticket data structure for ticket ID '{ticket_id_str}'"
                })

            ticket_status = str(ticket.get("status", "")).strip()
            if ticket_status == "deleted":
                return json.dumps({
                    "success": False,
                    "error": f"Cannot send email for ticket '{ticket_id_str}' with status 'deleted'"
                })

        if email_type_str == 'verification_request' and ticket_id_str:
            # Verification requests typically sent when ticket is resolved
            ticket = tickets_dict.get(ticket_id_str, {})
            ticket_status = str(ticket.get("status", "")).strip()
            valid_verification_statuses = ["resolved", "pending", "resolved_pending_verification"]

            if ticket_status not in valid_verification_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Email type 'verification_request' is not appropriate for ticket with status '{ticket_status}'. Expected status: {', '.join(valid_verification_statuses)}"
                })

        new_email_id = generate_id(emails_dict)

        new_email = {
            "email_id": new_email_id,
            "ticket_id": ticket_id_str,
            "template_id": None,
            "recipient_id": recipient_id_str,
            "subject": subject_str,
            "message_body": message_body_str,
            "email_type": email_type_str,
            "status": "sent",
            "sent_at": timestamp,
            "created_at": timestamp,
        }

        # Add email to dictionary
        emails_dict[new_email_id] = new_email

        # Prepare return data
        email_return = new_email.copy()
        email_return["recipient_email"] = recipient_email
        email_return["recipient_type"] = recipient_type

        if recipient_type == "user":
            email_return["recipient_name"] = f"{recipient.get('first_name', '')} {recipient.get('last_name', '')}".strip()
        elif recipient_type == "customer":
            email_return["recipient_name"] = recipient.get("customer_name", "")

        if ticket_id_str and ticket_id_str in tickets_dict:
            email_return["ticket_number"] = tickets_dict[ticket_id_str].get("ticket_number")

        # Build success message
        message = f"Email sent successfully to {recipient_email}"
        if ticket_id_str:
            ticket_number = tickets_dict.get(ticket_id_str, {}).get("ticket_number", ticket_id_str)
            message += f" regarding ticket '{ticket_number}'"

        return json.dumps({
            "success": True,
            "email": email_return,
            "message": message,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "send_email",
                "description": (
                    "Sends an email notification to a recipient regarding ticket updates, resolutions, or other support communications. "
                    "This function creates and delivers email messages to customers or internal users. "
                    "Use this to notify customers of ticket status changes, request verification of fixes, "
                    "send escalation notices to stakeholders, or deliver resolution confirmations. "
                    "Supports different email types including verification requests, status updates, escalation notices, and resolution notices."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipient_id": {
                            "type": "string",
                            "description": "The unique identifier of the recipient (can be a user ID or customer ID).",
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
                            "enum": ["verification_request", "status_update", "escalation_notice", "resolution_notice"]
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "Optional. The unique identifier of the ticket this email relates to.",
                        },
                    },
                    "required": ["recipient_id", "subject", "message_body", "email_type"],
                },
            },
        }
