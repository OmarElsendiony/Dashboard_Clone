import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class SendDraftEmail(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        email_id: str
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not email_id:
            return json.dumps({"success": False, "error": "Email ID is required"})

        # Check if the email exists
        emails = data.get("emails", {})
        email_id = str(email_id)
        if email_id not in emails:
            return json.dumps({
                "success": False,
                "error": f"Email with ID '{email_id}' does not exist"
            })
        attachments = data.get("attachments", {})
        # Here you would normally integrate with an email service to send the email.
        email_attachment = next((
            att for att in attachments.values() if att["draft_id"] == email_id), None)
        if emails[email_id]["status"] != "drafted":
            return json.dumps({
                "success": False,
                "error": f"Email with ID '{email_id}' is not in draft status and cannot be sent"
            })
        # Update the email status to 'sent'
        emails[email_id]["status"] = "sent"
        emails[email_id]["sent_at"] = "2026-02-02 23:59:00"

        return json.dumps({
            "success": True,
            "message": f"Email {email_id} sent successfully",
            "email": emails[email_id],
            "attachment": email_attachment
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "send_draft_email",
                "description": "Sends a previously created draft email to its designated recipients.  It should only be used after the draft content and any necessary attachments have been finalized.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_id": {
                            "type": "string",
                            "description": "The ID of the draft email to be sent."
                        }
                    },
                    "required": ["email_id"],
                }
            }
        }
