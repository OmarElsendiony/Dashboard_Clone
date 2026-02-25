import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class SearchPages(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        page_id: Optional[str] = None,
        document_id: Optional[str] = None,
        title: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for pages"
            })
        
        pages = data.get("pages", {})
        documents = data.get("documents", {})
        
        if not page_id and not document_id and not title:
            return json.dumps({
                "success": False,
                "error": "At least one parameter (page_id, document_id, or title) must be provided"
            })

        def build_page_data(pid, page):
            doc_id = page.get("document_id")
            document = documents.get(str(doc_id), {}) if doc_id else {}
            return {
                "page_id": str(pid),
                "document_id": str(doc_id) if doc_id is not None else None,
                "program_id": str(document.get("project_id")) if document.get("project_id") is not None else None,
                "title": str(page.get("title", "")) if page.get("title") is not None else None,
                "content": str(page.get("content", "")) if page.get("content") is not None else None,
                "created_at": str(page.get("created_at", "")) if page.get("created_at") is not None else None,
                "updated_at": str(page.get("updated_at", "")) if page.get("updated_at") is not None else None
            }
        
        if page_id:
            if str(page_id) not in pages:
                return json.dumps({
                    "success": False,
                    "error": f"Page with ID '{page_id}' not found"
                })
            
            page = pages[str(page_id)]
            
            if document_id and str(page.get("document_id")) != str(document_id):
                return json.dumps({
                    "success": False,
                    "error": f"Page does not belong to document '{document_id}'"
                })
                
            if title and str(page.get("title")) != str(title):
                return json.dumps({
                    "success": False,
                    "error": f"Page title is '{page.get('title')}', not '{title}'"
                })
            
            return json.dumps({
                "success": True,
                "page_data": build_page_data(page_id, page)
            })
        
        if title or document_id:
            found_pages = []
            
            for pid, page in pages.items():
                if title and str(page.get("title")) != str(title):
                    continue
                
                if document_id and str(page.get("document_id")) != str(document_id):
                    continue
                
                found_pages.append(build_page_data(pid, page))
            
            if not found_pages:
                return json.dumps({
                    "success": False,
                    "error": "No page found matching the specified filters"
                })
            
            if len(found_pages) == 1:
                return json.dumps({
                    "success": True,
                    "page_data": found_pages[0]
                })
            
            return json.dumps({
                "success": True,
                "multiple_results": True,
                "count": int(len(found_pages)),
                "pages": found_pages
            })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "search_pages",
                "description": "Searches for and retrieves wiki pages associated with documents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page_id": {
                            "type": "string",
                            "description": "The unique identifier of the page"
                        },
                        "document_id": {
                            "type": "string",
                            "description": "Filter results by parent document ID"
                        },
                        "title": {
                            "type": "string",
                            "description": "The exact title of the page"
                        }
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["page_id"]},
                        {"required": ["document_id"]},
                        {"required": ["title"]}
                    ]
                }
            }
        }