import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateKnowledgeArticle(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        title: str,
        description: Optional[str] = None,
        related_ticket_id: Optional[str] = None,
        doc_name: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not title:
            return json.dumps({"success": False, "error": "Missing Argument: 'title' is required."})

        title = str(title).strip()
        description = str(description).strip() if description else ""
        related_ticket_id = str(related_ticket_id).strip() if related_ticket_id else ""

        if not doc_name:
            doc_name = title.lower().replace(" ", "_").replace("-", "_").replace("[", "").replace("]", "")
        else:
            doc_name = str(doc_name).strip()

        documents = data.get("documents", {})
        if not isinstance(documents, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'documents' must be a dictionary"})

        max_id = 0
        for k in documents.keys():
            try:
                num = int(str(k))
                if num > max_id:
                    max_id = num
            except ValueError:
                continue

        for v in documents.values():
            if isinstance(v, dict):
                try:
                    num = int(str(v.get("document_id", "0")))
                    if num > max_id:
                        max_id = num
                except ValueError:
                    continue

        new_id = str(max_id + 1)
        timestamp = "2026-02-02 23:59:00"

        new_document = {
            "document_id": new_id,
            "doc_name": doc_name,
            "title": title,
            "description": description,
            "related_ticket_id": related_ticket_id,
            "space_key": "Drafts_Space",
            "status": "WIP",
            "created_at": timestamp,
            "updated_at": timestamp
        }

        documents[new_id] = new_document

        return json.dumps({
            "success": True,
            "document": new_document,
            "message": f"Knowledge article '{new_id}' created successfully in Drafts_Space."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_knowledge_article",
                "description": (
                    "Generates a new draft document in the knowledge base (documents table) and places it into the 'Drafts_Space' with a 'WIP' (Work in Progress) status.\n"
                    " Purpose: Facilitates the capture of new knowledge and missing documentation. Maps to the 'Draft Knowledge Articles' SOP (saving verified solutions from resolved tickets) and the 'Report Knowledge Gaps' SOP (creating blank placeholder documents for high-frequency topics).\n"
                    " When to use: Use this tool when you resolve a ticket with a non-trivial solution and need to document the steps (linking the ticket ID), or when you identify a knowledge gap and need to create a placeholder document titled '[REQUEST] - [Topic Name]'.\n"
                    " Returns: Returns a JSON string containing a success boolean, the newly created document dictionary object (with auto-generated ID, Drafts_Space assignment, and WIP status), and a success message."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the new knowledge article. For gaps, use the format '[REQUEST] - [Topic Name]'."
                        },
                        "description": {
                            "type": "string",
                            "description": "The body content of the document. Usually contains the verified solution steps. Can be left blank for knowledge gaps."
                        },
                        "related_ticket_id": {
                            "type": "string",
                            "description": "The unique identifier of the resolved support ticket this document is derived from. Required for 'Draft Knowledge Articles'."
                        },
                        "doc_name": {
                            "type": "string",
                            "description": "An optional URL-friendly internal name for the document. If omitted, one will be auto-generated from the title."
                        }
                    },
                    "required": ["title"]
                }
            }
        }
