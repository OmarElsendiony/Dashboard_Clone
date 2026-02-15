import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetPage(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        page_id: str,
        space_key: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        if not page_id:
            return json.dumps({
                "success": False,
                "error": "Missing Argument: 'page_id' is required."
            })

        documents = data.get("documents", {})

        if not isinstance(documents, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'documents' must be a dictionary"
            })

        doc_key = str(page_id)

        page = documents.get(doc_key)

        if page is None:
            for v in documents.values():
                if isinstance(v, dict) and str(v.get("page_id", "")) == doc_key:
                    page = v
                    break

        if page is None:
            return json.dumps({
                "success": False,
                "error": f"Not Found Error: page_id '{page_id}' not found."
            })

        if space_key is not None and str(page.get("space_key", "")) != str(space_key):
            return json.dumps({
                "success": False,
                "error": (
                    f"Not Found Error: page_id '{page_id}' not found in space '{space_key}'."
                )
            })

        body = page.get("description", "")

        page_output = dict(page)

        if "document_id" in page_output:
            page_output["page_id"] = str(page_output.pop("document_id"))
        else:
            page_output["page_id"] = str(page_id)

        return json.dumps({
            "success": True,
            "page": page_output,
            "body": body,
            "message_text": "Page retrieved successfully."
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_page",
                "description": (
                    "Retrieves a single knowledge base page by page ID and returns its full body content as stored "
                    "(Markdown or storage format). Use this when you need the exact page content for troubleshooting, "
                    "incident context, documentation review, or linking a ticket to a specific internal page."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page_id": {
                            "type": "string",
                            "description": "Unique page identifier."
                        },
                        "space_key": {
                            "type": "string",
                            "enum": ["Drafts_Space", "Public_KB_Space"],
                            "description": "Knowledge base space key (optional )."
                        }
                    },
                    "required": ["page_id"]
                }
            }
        }
