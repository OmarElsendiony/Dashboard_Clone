import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool

class GetDocuments(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        document_type: Optional[str] = None,
        document_url: Optional[str] = None,
        title: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """
        Get document(s) for an employee based on filter criteria.
        Returns all documents that match the specified filters.
        """
        documents = data.get("documents", {})
        employees = data.get("employees", {})
        results = []
        
        # Validate required field
        if not employee_id:
            return json.dumps({
                "success": False,
                "error": "employee_id is required",
                "count": 0,
                "documents": []
            })
        
        # Validate employee exists
        if employee_id not in employees:
            return json.dumps({
                "success": False,
                "error": f"employee_id '{employee_id}' does not reference a valid employee",
                "count": 0,
                "documents": []
            })
        
        # Validate document_type if provided
        if document_type:
            valid_document_types = ["onboarding", "offboarding", "employee", "payroll_input", "payroll_earning", "payroll_deduction", "payslip"]
            if document_type not in valid_document_types:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid document_type. Must be one of: {', '.join(valid_document_types)}",
                    "count": 0,
                    "documents": []
                })
        
        # Validate status if provided
        if status:
            valid_statuses = ["accepted", "rejected"]
            if status not in valid_statuses:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                    "count": 0,
                    "documents": []
                })
        
        # Filter documents
        for doc_id, document in documents.items():
            match = True
            
            # employee_id is required filter
            if document.get("employee_id") != employee_id:
                match = False
            
            if document_type and document.get("document_type") != document_type:
                match = False
            if document_url and document.get("document_url") != document_url:
                match = False
            if title and document.get("title") != title:
                match = False
            if status and document.get("status") != status:
                match = False
            
            if match:
                # Create a copy of the document to avoid modifying the original
                doc_copy = document.copy()
                results.append(doc_copy)
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "documents": results
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_documents",
                "description": "Get document(s) for an employee based on filter criteria. Returns all documents that match the specified filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Employee ID (required)"
                        },
                        "document_type": {
                            "type": "string",
                            "description": "Filter by document type: onboarding, offboarding, employee, payroll_input, payroll_earning, payroll_deduction, payslip (optional)",
                            "enum": ["onboarding", "offboarding", "employee", "payroll_input", "payroll_earning", "payroll_deduction", "payslip"]
                        },
                        "document_url": {
                            "type": "string",
                            "description": "Filter by document URL (optional)"
                        },
                        "title": {
                            "type": "string",
                            "description": "Filter by document title (optional)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status: accepted, rejected (optional)",
                            "enum": ["accepted", "rejected"]
                        }
                    },
                    "required": ["employee_id"]
                }
            }
        }
