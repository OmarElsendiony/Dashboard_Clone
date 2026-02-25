import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ManagePage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        title: str,
        content: str,
        document_id: str,
    ) -> str:
        timestamp = "2026-02-11T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        for param_name, param_value in [
            ("title", title),
            ("content", content),
            ("document_id", document_id),
        ]:
            if param_value is None or not str(param_value).strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Missing required parameter: '{param_name}'",
                    }
                )

        title_str = str(title).strip()
        content_str = str(content).strip()
        document_id_str = str(document_id).strip()

        documents_dict = data.get("documents", {})
        pages_dict = data.get("pages", {})

        if document_id_str not in documents_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Document with ID '{document_id_str}' not found",
                }
            )

        document = documents_dict[document_id_str]
        if not isinstance(document, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Invalid document data structure for ID '{document_id_str}'"
                    ),
                }
            )

        document_status = str(document.get("status", "")).strip().lower()
        if document_status not in ["active"]:
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Document '{document_id_str}' has status '{document_status}'. "
                        "Only documents with status 'active' can have pages created or updated."
                    ),
                }
            )

        existing_page_id = None
        for p_id, p_data in pages_dict.items():
            if not isinstance(p_data, dict):
                continue
            if (
                str(p_data.get("document_id", "")).strip() == document_id_str
                and str(p_data.get("title", "")).strip().lower() == title_str.lower()
            ):
                existing_page_id = p_id
                break

        page_created = False

        if existing_page_id:
            page = pages_dict[existing_page_id]
            page["content"] += "\n" + str(content_str)
            page["updated_at"] = timestamp

            page_id_str = existing_page_id

            response_message = f"Page '{title_str}' updated successfully in document '{document_id_str}'"

        else:
            new_page_id = generate_id(pages_dict)

            new_page = {
                "page_id": str(new_page_id),
                "document_id": str(document_id_str),
                "title": str(title_str),
                "content": str(content_str),
                "type": None,
                "status": None,
                "created_at": timestamp,
                "updated_at": timestamp,
            }

            pages_dict[new_page_id] = new_page
            page_id_str = new_page_id
            page_created = True

            response_message = f"Page '{title_str}' created successfully in document '{document_id_str}'"

        return json.dumps(
            {
                "success": True,
                "page": pages_dict[page_id_str],
                "page_created": page_created,
                "message": str(response_message),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "manage_page",
                "description": "Creates a new page or updates an existing page within a document. "
                "If a page with the specified title already exists in the document, "
                "its content is updated. If no such page exists, a new page is created. "
                "Use this to maintain structured documentation across workflows: "
                "documenting blockers, tracking project status summaries, capturing scope "
                "change proposals, and recording project closure summaries. "
                "Page titles are case-insensitive when checking for existence within a document.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the page.",
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write to the page.",
                        },
                        "document_id": {
                            "type": "string",
                            "description": "The unique identifier of the document to add or update the page in.",
                        },
                    },
                    "required": ["title", "content", "document_id"],
                },
            },
        }
