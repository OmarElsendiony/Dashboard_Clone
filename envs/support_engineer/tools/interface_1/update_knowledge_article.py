import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateKnowledgeArticle(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        page_id: str,
        new_page_name: Optional[str] = None,
        new_title: Optional[str] = None,
        new_description: Optional[str] = None,
        new_related_ticket_id: Optional[str] = None,
        new_space_key: Optional[str] = None,
        new_status: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not page_id:
            return json.dumps({"success": False, "error": "Missing Argument: 'page_id' is required."})

        page_id_str = str(page_id).strip()

        if (
            new_page_name is None
            and new_title is None
            and new_description is None
            and new_related_ticket_id is None
            and new_space_key is None
            and new_status is None
        ):
            return json.dumps({
                "success": False,
                "error": "Invalid Argument: At least one update field must be provided."
            })

        valid_space_keys = ["Drafts_Space", "Public_KB_Space"]
        if new_space_key is not None:
            if str(new_space_key).strip() not in valid_space_keys:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid Argument: new_space_key must be one of {valid_space_keys}."
                })

        valid_statuses = ["WIP", "verified"]
        if new_status is not None:
            status_lower = str(new_status).strip().lower()
            if status_lower == "wip":
                new_status = "WIP"
            elif status_lower == "verified":
                new_status = "verified"
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid Argument: new_status must be one of {valid_statuses} (case-insensitive mapping supported)."
                })

        documents = data.get("documents", {})
        if not isinstance(documents, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'documents' must be a dictionary"})

        target_doc = None
        for v in documents.values():
            if isinstance(v, dict) and str(v.get("document_id", "")).strip() == page_id_str:
                target_doc = v
                break

        if not target_doc:
            return json.dumps({"success": False, "error": f"Not Found Error: page_id (document_id) '{page_id_str}' not found."})

        timestamp = "2026-02-02 23:59:00"
        is_change_detected = False

        if new_page_name is not None and target_doc.get("doc_name") != str(new_page_name).strip():
            target_doc["doc_name"] = str(new_page_name).strip()
            is_change_detected = True

        if new_title is not None and target_doc.get("title") != str(new_title).strip():
            target_doc["title"] = str(new_title).strip()
            is_change_detected = True

        if new_description is not None and target_doc.get("description") != str(new_description):
            target_doc["description"] = str(new_description)
            is_change_detected = True

        if new_related_ticket_id is not None and str(target_doc.get("related_ticket_id", "")) != str(new_related_ticket_id).strip():
            target_doc["related_ticket_id"] = str(new_related_ticket_id).strip()
            is_change_detected = True

        if new_space_key is not None and target_doc.get("space_key") != str(new_space_key).strip():
            target_doc["space_key"] = str(new_space_key).strip()
            is_change_detected = True

        if new_status is not None and target_doc.get("status") != new_status:
            target_doc["status"] = new_status
            is_change_detected = True

        if is_change_detected:
            target_doc["updated_at"] = timestamp

            safe_doc_response = {
                "page_id": str(target_doc.get("document_id", "")),
                "page_name": str(target_doc.get("doc_name", "")),
                "title": str(target_doc.get("title", "")),
                "description": str(target_doc.get("description", "")),
                "related_ticket_id": str(target_doc.get("related_ticket_id", "")),
                "space_key": str(target_doc.get("space_key", "")),
                "status": str(target_doc.get("status", "")),
                "created_at": str(target_doc.get("created_at", "")),
                "updated_at": str(target_doc.get("updated_at", ""))
            }

            return json.dumps({
                "success": True,
                "document": safe_doc_response,
                "message": f"Knowledge base article '{page_id_str}' updated successfully."
            })
        else:
            return json.dumps({
                "success": False,
                "error": "No update Detected",
                "message": f"No-Op: Article '{page_id_str}' already has the provided values. No update performed."
            })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_knowledge_article",
                "description": (
                    "Updates an existing Knowledge Base article by modifying its content, metadata, or lifecycle states."
                    " Purpose: Facilitates the 'Verify and Publish Knowledge Articles' SOP. Specifically used to move a document from the 'Drafts_Space' to the 'Public_KB_Space' and change its status to 'verified' once all structure and sanity checks pass."
                    " When to use: Use this tool to verify and publish a knowledge article, update an existing article's title/description, change its URL-friendly page name, or link it to a different support ticket. 'page_id' is strictly the identifier and cannot be changed."
                    " Returns: Returns a JSON string containing a success boolean, the updated document object (with keys formatted as page_id and page_name), and a success message. Fails if the provided page_id does not exist or if invalid enums are supplied."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page_id": {
                            "type": "string",
                            "description": "The strict, immutable unique identifier (document_id) of the Knowledge Base article to update. This value cannot be changed. Required."
                        },
                        "new_page_name": {
                            "type": "string",
                            "description": "The updated URL-friendly internal name for the article (maps to doc_name). Optional."
                        },
                        "new_title": {
                            "type": "string",
                            "description": "The updated title of the Knowledge Base article. Optional."
                        },
                        "new_description": {
                            "type": "string",
                            "description": "The updated body content/text of the article. Optional."
                        },
                        "new_related_ticket_id": {
                            "type": "string",
                            "description": "The updated identifier of the support ticket associated with this article. Optional."
                        },
                        "new_space_key": {
                            "type": "string",
                            "enum": ["Drafts_Space", "Public_KB_Space"],
                            "description": "The updated documentation space where this page resides. Change to 'Public_KB_Space' when publishing. Optional."
                        },
                        "new_status": {
                            "type": "string",
                            "enum": ["WIP", "verified"],
                            "description": "The updated publication status of the article. Change to 'verified' when publishing. Optional."
                        }
                    },
                    "required": ["page_id"]
                }
            }
        }
