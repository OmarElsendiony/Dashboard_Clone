import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreateDraftMail(Tool):
    @staticmethod
    def invoke(
            data: Dict[str, Any],
            ticket_id: str,
            to_email: str,
            subject: str,
            message_body: str,
            email_type: str = "status_update",
            status: str = "drafted",
            recipient_type: str = "customer"
        ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            return str(max([int(k) for k in table.keys()], default=0) + 1)
        # 1. Basic data integrity check
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not ticket_id:
            return json.dumps({"success": False, "error": "Ticket ID is required"})

        if not to_email:
            return json.dumps({"success": False, "error": "Recipient email is required"})

        if not subject:
            return json.dumps({"success": False, "error": "Email subject is required"})

        if not message_body:
            return json.dumps({"success": False, "error": "Email message body is required"})

        # 2. Validation: Enum for email_type
        valid_email_types = ['verification_request', 'status_update', 'escalation_notice', 'resolution_notice']
        if email_type.lower() not in valid_email_types:
            return json.dumps({
                "success": False,
                "error": f"Invalid email_type. Must be one of {valid_email_types}"
            })

        # 3. Validation: Enum for status
        if status.lower() != 'drafted':
            return json.dumps({
                "success": False,
                "error": f"Invalid status. Must be 'drafted'"
            })
        if recipient_type not in ['customer', 'user']:
            return json.dumps({
                "success": False,
                "error": "Invalid recipient_type. Must be either 'customer' or 'user'"
            })
        # validate the ticket_id
        tickets = data.get("tickets", {})
        if ticket_id not in tickets:
            return json.dumps({
                "success": False,
                "error": f"Ticket with ID '{ticket_id}' does not exist"
            })
        # validate the recipient_id
        recipients = data.get(f"{recipient_type}s", {})
        recipient_id = None
        for r_id, r_info in recipients.items():
            if r_info.get("email") == to_email:
                recipient_id = r_id
                break

        if recipient_id is None:
            return json.dumps({
                "success": False,
                "error": f"Recipient with email '{to_email}' does not exist"
            })

        # 4. Logic: Create the new email object
        if "emails" not in data:
            data["emails"] = {}

        # Simple ID generation based on current count
        new_email_id = generate_id(data["emails"])

        new_email = {
            "email_id": new_email_id,
            "ticket_id": str(ticket_id),
            "template_id": None,
            "recipient_id": str(recipient_id),
            "subject": subject[:500],  # Ensure varchar(500) constraint
            "message_body": message_body,
            "email_type": email_type,
            "status": status,
            "sent_at": None,
            "created_at": "2026-02-02 23:59:00"
        }

        data["emails"][new_email_id] = new_email

        return json.dumps({
            "success": True,
            "message": "Draft email created successfully",
            "email": new_email
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_draft_mail",
                "description": "Initializes a new email record in the system, specifically tailored for a given ticket. Use when preparing outgoing communications like status updates, verification requests, or resolution notices.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The ID of the ticket this email belongs to."
                        },
                        "to_email": {
                            "type": "string",
                            "description": "The email address of the recipient."
                        },
                        "subject": {
                            "type": "string",
                            "description": "The subject line of the email."
                        },
                        "message_body": {
                            "type": "string",
                            "description": "The main content of the email."
                        },
                        "email_type": {
                            "type": "string",
                            "enum": ["verification_request", "status_update", "escalation_notice", "resolution_notice"],
                            "description": "The category/type of the email."
                        },
                        "status": {
                            "type": "string",
                            "enum": ["drafted", "sent", "failed"],
                            "default": "drafted",
                            "description": "The current state of the email."
                        },
                        "recipient_type": {
                            "type": "string",
                            "enum": ["customer", "user"],
                            "default": "customer",
                            "description": "The type of recipient (customer or user)."
                        },
                    },
                    "required": ["ticket_id", "to_email", "subject", "message_body"]
                }
            }
        }
