import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetDoc(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        document_id: Optional[str] = None,
        title: Optional[str] = None,
        program_id: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for documents"
            })
        
        documents = data.get("documents", {})
        
        if not document_id and not title and not program_id:
            return json.dumps({
                "success": False,
                "error": "At least one parameter (document_id, title, or program_id) must be provided"
            })
        
        if document_id:
            if str(document_id) not in documents:
                return json.dumps({
                    "success": False,
                    "error": f"Document with ID '{document_id}' not found"
                })
            
            document = documents[str(document_id)]
            
            if program_id and str(document.get("project_id")) != str(program_id):
                return json.dumps({
                    "success": False,
                    "error": f"Document does not belong to program '{program_id}'"
                })
                
            if title and str(document.get("title")) != str(title):
                return json.dumps({
                    "success": False,
                    "error": f"Document title is '{document.get('title')}', not '{title}'"
                })
            
            document_data = {
                "document_id": str(document_id),
                "title": str(document.get("title", "")) if document.get("title") is not None else None,
                "body": str(document.get("body", "")) if document.get("body") is not None else None,
                "status": str(document.get("status", "")) if document.get("status") is not None else None,
                "program_id": str(document.get("project_id", "")) if document.get("project_id") is not None else None,
                "created_by": str(document.get("created_by", "")) if document.get("created_by") is not None else None,
                "updated_by": str(document.get("updated_by", "")) if document.get("updated_by") is not None else None,
                "created_at": str(document.get("created_at", "")) if document.get("created_at") is not None else None,
                "updated_at": str(document.get("updated_at", "")) if document.get("updated_at") is not None else None
            }
            
            return json.dumps({
                "success": True,
                "document_data": document_data
            })
        
        if title or program_id:
            found_documents = []
            
            for did, document in documents.items():
                if title and str(document.get("title")) != str(title):
                    continue
                
                if program_id and str(document.get("project_id")) != str(program_id):
                    continue
                
                document_data = {
                    "document_id": str(did),
                    "title": str(document.get("title", "")) if document.get("title") is not None else None,
                    "body": str(document.get("body", "")) if document.get("body") is not None else None,
                    "status": str(document.get("status", "")) if document.get("status") is not None else None,
                    "program_id": str(document.get("project_id", "")) if document.get("project_id") is not None else None,
                    "created_by": str(document.get("created_by", "")) if document.get("created_by") is not None else None,
                    "updated_by": str(document.get("updated_by", "")) if document.get("updated_by") is not None else None,
                    "created_at": str(document.get("created_at", "")) if document.get("created_at") is not None else None,
                    "updated_at": str(document.get("updated_at", "")) if document.get("updated_at") is not None else None
                }
                found_documents.append(document_data)
            
            if not found_documents:
                return json.dumps({
                    "success": False,
                    "error": "No document found matching the specified filters"
                })
            
            if len(found_documents) == 1:
                return json.dumps({
                    "success": True,
                    "document_data": found_documents[0]
                })
            
            return json.dumps({
                "success": True,
                "multiple_results": True,
                "count": int(len(found_documents)),
                "documents": found_documents
            })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_doc",
                "description": "Retrieves document information. Use this to find design documents, specifications, runbooks, postmortems, meeting notes, or reports. Helps locate project documentation for reference, review, or sharing with stakeholders.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "The unique identifier of the document"
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the document"
                        },
                        "program_id": {
                            "type": "string",
                            "description": "Filter results by program ID"
                        }
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["document_id"]},
                        {"required": ["title"]},
                        {"required": ["program_id"]}
                    ]
                }
            }
        }
