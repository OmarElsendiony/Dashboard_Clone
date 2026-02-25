import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateWorkDocument(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        title: str,
        creator_id: str,
        doc_type: str = "general",
        project_id: Optional[str] = None,
        incident_id: Optional[str] = None,
        initial_content: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if len(title) > 500:
            return json.dumps(
                {
                    "success": False,
                    "error": "Title must be at most 500 characters long.",
                }
            )

        now = "2026-02-11T23:59:00"

        documents = data.get("documents", {})
        pages = data.get("pages", {})
        users = data.get("users", {})
        projects = data.get("projects", {})
        incidents = data.get("incidents", {})

        def generate_id(table: Dict[str, Any]) -> str:
            return str(max([int(k) for k in table.keys()], default=0) + 1)

        # 2. Validation: Creator Existence
        if creator_id not in users:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Creator ID '{creator_id}' not found in registry.",
                }
            )

        # 3. Validation: Project ID if provided
        if project_id is not None:
            project_found = False
            for _proj_key, proj_data in projects.items():
                if str(proj_data.get("project_id")) == str(project_id):
                    project_found = True
                    break
            if not project_found:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Project ID '{project_id}' not found.",
                    }
                )

        # 4. Validation: Incident ID if provided
        if incident_id is not None:
            if incident_id not in incidents:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Incident ID '{incident_id}' not found.",
                    }
                )

        # 5. Validation: Enum for Page/Doc Type
        valid_types = [
            "product_requirement_document",
            "post_incident_review",
            "root_cause_analysis",
            "retrospective",
            "general",
        ]
        if doc_type not in valid_types:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid doc_type. Must be one of {valid_types}",
                }
            )

        # 6. Logic: Create the Document record (the container)
        new_doc_id = generate_id(documents)
        new_doc = {
            "document_id": new_doc_id,
            "title": title,
            "project_id": project_id,
            "incident_id": incident_id,
            "status": "active",
            "created_by": creator_id,
            "updated_by": creator_id,
            "created_at": now,
            "updated_at": now,
        }
        documents[new_doc_id] = new_doc

        # 7. Logic: Create initial Page (always created to ensure document content exists)
        new_page_id = generate_id(pages)
        new_page = {
            "page_id": new_page_id,
            "document_id": new_doc_id,
            "title": title,
            "content": "",
            "type": doc_type,
            "status": "draft",
            "created_at": now,
            "updated_at": now,
        }

        # Apply templates or user-provided content
        if initial_content or doc_type != "general":
            content = initial_content or f"Draft template for {doc_type}."

            # Enforce Content Format Standard for RCAs per Knowledge Governance
            if doc_type == "root_cause_analysis" and "Context:" not in content:
                content = "Context: [Draft] | Key Decisions: [Pending] | Stakeholders Involved: [Pending] | Status: Draft"

            new_page["content"] = content

        pages[new_page_id] = new_page

        # Type cast all values and build response object
        typed_doc = {}
        for key, value in new_doc.items():
            if value is None:
                typed_doc[key] = None
            elif key in [
                "document_id",
                "title",
                "project_id",
                "incident_id",
                "status",
                "created_by",
                "updated_by",
                "created_at",
                "updated_at",
            ]:
                typed_doc[key] = str(value) if value is not None else None
            elif isinstance(value, bool):
                typed_doc[key] = bool(value)
            elif isinstance(value, int):
                typed_doc[key] = int(value)
            elif isinstance(value, float):
                typed_doc[key] = float(value)
            elif isinstance(value, list):
                typed_doc[key] = list(value)
            elif isinstance(value, dict):
                typed_doc[key] = dict(value)
            else:
                typed_doc[key] = value

        typed_pages = []
        for page in [new_page]:
            typed_page = {}
            for page_key, page_value in page.items():
                if page_value is None:
                    typed_page[page_key] = None
                elif page_key in [
                    "page_id",
                    "document_id",
                    "title",
                    "content",
                    "type",
                    "status",
                    "created_at",
                    "updated_at",
                ]:
                    typed_page[page_key] = (
                        str(page_value) if page_value is not None else None
                    )
                elif isinstance(page_value, bool):
                    typed_page[page_key] = bool(page_value)
                elif isinstance(page_value, int):
                    typed_page[page_key] = int(page_value)
                elif isinstance(page_value, float):
                    typed_page[page_key] = float(page_value)
                elif isinstance(page_value, list):
                    typed_page[page_key] = list(page_value)
                elif isinstance(page_value, dict):
                    typed_page[page_key] = dict(page_value)
                else:
                    typed_page[page_key] = page_value
            typed_pages.append(typed_page)

        response = {
            "success": bool(True),
            "message": str(f"Work document '{title}' created successfully."),
            "document": dict(typed_doc),
            "pages": list(typed_pages),
        }

        return json.dumps(response)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_work_document",
                "description": "Initializes technical documentation containers and their primary content pages within the project knowledge base, supporting the generation of Pivot Logs for roadmap shifts or Root Cause Analysis templates for incident resolution while ensuring adherence to mandatory content format standards.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "maxLength": 500,
                            "description": "The formal title of the document (max 500 characters).",
                        },
                        "creator_id": {
                            "type": "string",
                            "description": "The user_id of the author initializing the document.",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "The unique ID of the associated project.",
                        },
                        "incident_id": {
                            "type": "string",
                            "description": "The unique ID of the associated incident.",
                        },
                        "initial_content": {
                            "type": "string",
                            "description": "The starting text or data to populate the first page.",
                        },
                        "doc_type": {
                            "type": "string",
                            "enum": [
                                "product_requirement_document",
                                "post_incident_review",
                                "root_cause_analysis",
                                "retrospective",
                                "general",
                            ],
                            "default": "general",
                            "description": "The document category which dictates the audit template and governance context.",
                        },
                    },
                    "required": ["title", "creator_id"],
                },
            },
        }
