import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UploadWorkerDocument(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        employee_id: str,
        document_url: str,
        title: Optional[str] = None,
        document_type: Optional[str] = None,
        target_entity: Optional[str] = None,
        entity_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        """
        Upload a worker document record into the Workday dataset.
        All inputs are text fields; file uploads are not required.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        timestamp = "2025-12-12T12:00:00"

        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format", "halt": True}
            )

        employees = data.get("employees", {})
        documents = data.get("documents", {})

        # Validate required parameters
        if not all([employee_id, document_url, document_type]):
            return json.dumps(
                {
                    "success": False,
                    "error": "Missing required parameters: employee_id, document_url, document_type",
                    "halt": True,
                }
            )

        if not isinstance(employees, dict) or employee_id not in employees:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Employee '{employee_id}' not found",
                    "halt": True,
                }
            )

        allowed_document_types = [
            "onboarding",
            "offboarding",
            "employee",
            "payroll_input",
            "payroll_earning",
            "payroll_deduction",
            "payslip",
        ]
        if document_type not in allowed_document_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid document_type. Must be one of {allowed_document_types}",
                    "halt": True,
                }
            )

        allowed_status_values = ["accepted", "rejected"]
        if status is not None and status not in allowed_status_values:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid status. Must be one of {allowed_status_values}",
                    "halt": True,
                }
            )

        allowed_entity_types = [
            "employee",
            "onboarding",
            "offboarding",
            "payroll_input",
            "payroll_earning",
            "payroll_deduction",
            "payslip",
        ]
        if entity_type is None:
            entity_type = "employee"
        elif entity_type not in allowed_entity_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid entity_type. Must be one of {allowed_entity_types}",
                    "halt": True,
                }
            )

        if target_entity is None:
            target_entity = employee_id

        # Prevent duplicate uploads for the same employee, URL, and document type
        for document in documents.values():
            if (
                document.get("employee_id") == employee_id
                and document.get("document_url") == document_url
                and document.get("document_type") == document_type
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Duplicate document detected for this employee with the same URL and document_type",
                        "halt": True,
                    }
                )

        document_id = generate_id(documents)
        normalized_title = (
            title
            if title
            else f"{document_type.replace('_', ' ').title()} Document"
        )

        document_record = {
            "document_id": document_id,
            "employee_id": employee_id,
            "document_url": document_url,
            "title": normalized_title,
            "document_type": document_type,
            "target_entity": target_entity,
            "entity_type": entity_type,
            "status": status if status else "accepted",
            "created_at": timestamp,
            "last_updated": timestamp,
        }

        documents[document_id] = document_record

        return json.dumps({"success": True, **document_record})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "upload_worker_document",
                "description": (
                    "Upload a worker-related document record (text-only input; "
                    "no file uploads). Requires employee_id, document_url, and "
                    "document_type. Optionally supply title, target_entity, "
                    "entity_type, and status."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "employee_id": {
                            "type": "string",
                            "description": "Worker ID the document belongs to",
                        },
                        "document_url": {
                            "type": "string",
                            "description": "Text URL/location of the stored document",
                        },
                        "title": {
                            "type": "string",
                            "description": "Document title; defaults to '<Document Type> Document'",
                        },
                        "document_type": {
                            "type": "string",
                            "description": "Document classification (onboarding, offboarding, employee, payroll_input, payroll_earning, payroll_deduction, payslip)",
                            "enum": [
                                "onboarding",
                                "offboarding",
                                "employee",
                                "payroll_input",
                                "payroll_earning",
                                "payroll_deduction",
                                "payslip",
                            ],
                        },
                        "target_entity": {
                            "type": "string",
                            "description": "Entity identifier the document references; defaults to employee_id",
                        },
                        "entity_type": {
                            "type": "string",
                            "description": "Type of entity referenced (employee, onboarding, offboarding, payroll_input, payroll_earning, payroll_deduction, payslip); defaults to employee",
                            "enum": [
                                "employee",
                                "onboarding",
                                "offboarding",
                                "payroll_input",
                                "payroll_earning",
                                "payroll_deduction",
                                "payslip",
                            ],
                        },
                        "status": {
                            "type": "string",
                            "description": "Document review status; defaults to accepted",
                            "enum": ["accepted", "rejected"],
                        },
                    },
                    "required": ["employee_id", "document_url", "document_type"],
                },
            },
        }
