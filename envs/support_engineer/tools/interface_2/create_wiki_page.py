import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateWikiPage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        title: str,
        description: str,
        space_key: str,
        related_ticket_id: Optional[str] = None,
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

        if not title:
            return json.dumps({"success": False, "error": "Missing required parameter: 'title'"})

        if not description:
            return json.dumps({"success": False, "error": "Missing required parameter: 'description'"})

        if not space_key:
            return json.dumps({"success": False, "error": "Missing required parameter: 'space_key'"})

        documents_dict = data.get("documents", {})
        tickets_dict = data.get("tickets", {})

        title_str = str(title).strip()
        description_str = str(description).strip()
        space_key_str = str(space_key).strip()
        related_ticket_id_str = (
            str(related_ticket_id).strip() if related_ticket_id else None
        )

        if not title_str:
            return json.dumps({"success": False, "error": "Title cannot be empty"})

        if not description_str:
            return json.dumps(
                {"success": False, "error": "Description cannot be empty"}
            )

        if not space_key_str:
            return json.dumps({"success": False, "error": "Space key cannot be empty"})

        valid_space_keys = ["Drafts_Space", "Public_KB_Space"]

        if space_key_str not in valid_space_keys:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid space_key '{space_key_str}'. Must be one of: {', '.join(valid_space_keys)}",
                }
            )

        if related_ticket_id_str:
            if related_ticket_id_str not in tickets_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Related ticket with ID '{related_ticket_id_str}' not found",
                    }
                )

            ticket = tickets_dict[related_ticket_id_str]

            if not isinstance(ticket, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid ticket data structure for ticket ID '{related_ticket_id_str}'",
                    }
                )

            ticket_status = str(ticket.get("status", "")).strip()
            if ticket_status == "deleted":
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Cannot link to ticket '{related_ticket_id_str}' with status 'deleted'",
                    }
                )

        for doc_id, doc in documents_dict.items():
            if not isinstance(doc, dict):
                continue

            if (
                str(doc.get("space_key", "")).strip() == space_key_str
                and str(doc.get("title", "")).strip() == title_str
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Document with title '{title_str}' already exists in space '{space_key_str}' (document_id: {doc_id})",
                    }
                )

        new_document_id = generate_id(documents_dict)

        initial_status = "WIP"

        new_document = {
            "document_id": str(new_document_id) if new_document_id else None,
            "title": str(title_str) if title_str else None,
            "description": str(description_str) if description_str else None,
            "related_ticket_id": str(related_ticket_id_str) if related_ticket_id_str else None,
            "space_key": str(space_key_str) if space_key_str else None,
            "status": str(initial_status) if initial_status else None,
            "created_at": timestamp,
            "updated_at": timestamp,
        }

        documents_dict[new_document_id] = new_document

        document_return = new_document.copy()

        if related_ticket_id_str and related_ticket_id_str in tickets_dict:
            ticket = tickets_dict[related_ticket_id_str]
            if isinstance(ticket, dict):
                document_return["ticket_number"] = str(ticket.get("ticket_number")) if ticket.get("ticket_number") else None

        message = f"Wiki page '{title_str}' created successfully in '{space_key_str}'"
        if related_ticket_id_str:
            ticket_number = tickets_dict.get(related_ticket_id_str, {}).get(
                "ticket_number", related_ticket_id_str
            )
            message += f" (linked to ticket '{ticket_number}')"

        return json.dumps(
            {
                "success": True,
                "document": document_return,
                "message": message,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_wiki_page",
                "description": (
                    "Creates a new wiki page or knowledge base document for capturing solutions, post-incident reviews, or troubleshooting guides. "
                    "This function creates documentation that can be used for future reference and knowledge sharing. "
                    "Use this to document ticket resolutions and fixes, create post-incident reviews after major incidents, "
                    "capture troubleshooting procedures and solutions, build knowledge base articles for common issues, "
                    "or record lessons learned from support cases. "
                    "Documents can be created in draft space for work-in-progress content or public knowledge base space for verified solutions."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the wiki page or document.",
                        },
                        "description": {
                            "type": "string",
                            "description": "The content/body of the wiki page describing the solution, review, or information.",
                        },
                        "space_key": {
                            "type": "string",
                            "description": "The space where the document will be created.",
                            "enum": ["Drafts_Space", "Public_KB_Space"],
                        },
                        "related_ticket_id": {
                            "type": "string",
                            "description": "Optional. The unique identifier of the ticket this documentation relates to for traceability.",
                        },
                    },
                    "required": ["title", "description", "space_key"],
                },
            },
        }
