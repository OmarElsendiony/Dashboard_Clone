import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class AddMailAttachment(Tool):
    @staticmethod
    def invoke(
            data: Dict[str, Any],
            email_id: str,
            file_name: str,
            file_path: str,
            repository_id: str
        ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            return str(max([int(k) for k in table.keys()], default=0) + 1)
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not email_id:
            return json.dumps({"success": False, "error": "Email ID is required"})

        # Check if the email exists
        emails = data.get("emails", {})
        files = data.get("files", {})
        if email_id not in emails:
            return json.dumps({
                "success": False,
                "error": f"Email with ID '{email_id}' does not exist"
            })
        attachments = data.get("attachments", {})
        # Update the email with attachment information
        new_attachment_id = generate_id(attachments)
        # Verify that the email is still in draft status before allowing attachments to be added
        if emails[email_id]["status"] != "drafted":
            return json.dumps({
                "success": False,
                "error": f"Email with ID '{email_id}' is not in draft status and cannot have attachments added"
            })
        if not file_name:
            return json.dumps({"Success": False, "Message": f"Filename is required."})
        if not file_path:
            return json.dumps({"Success": False, "Message": f"Filepath is required"})
        if not repository_id:
            return json.dumps({"Success": False, "Message": "Repository ID is required"})
        # verify that the file exists in the files dictionary with the file name and file path
        target_file = next((file for file in files.values() if file_name and file["file_name"] == file_name and file_path and file["file_path"] == file_path and repository_id == file["repository_id"]), None)
        if not target_file:
            return json.dumps({"Success": False, "Message": f"File with filename {file_name} and filepath {file_path} does not exists"})
        # Verify existing attachment
        existing_attachment = next((att for att in attachments.values() if att["draft_id"] == email_id and att["file_path"] == file_path and att["file_name"] == file_name), None)
        if existing_attachment:
            return json.dumps({"Success": False, "Message": f"Attachment with email_id {email_id}, filename {file_name} and filepath {file_path} already exists."})
        new_attachment = {
            "attachment_id": new_attachment_id,
            "draft_id": str(email_id),
            "file_name": str(file_name),
            "file_path": str(file_path),
            "created_at": "2026-02-02 23:59:00"
        }

        # Update the attachments dictionary with the new attachment
        data["attachments"][new_attachment_id] = new_attachment

        return json.dumps({
            "success": True,
            "message": f"Attachment added to email {email_id}",
            "attachment": new_attachment
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_mail_attachment",
                "description": "Appends a file attachment to an existing draft email. This tool should be used after a draft has been created but before it is sent.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_id": {
                            "type": "string",
                            "description": "The ID of the email to which the attachment is being added."
                        },
                        "file_name": {
                            "type": "string",
                            "description": "The name of the file being attached."
                        },
                        "file_path": {
                            "type": "string",
                            "description": "The path where the file is located."
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "The repository where to locate the file to be attached to the draft mail."
                        }
                    },
                    "required": ["email_id", "file_name", "file_path", "repository_id"]
                }
            }
        }
