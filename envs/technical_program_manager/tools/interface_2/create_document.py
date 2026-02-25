import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreateDocument(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        title: str,
        status: str,
        project_id: str,
        created_by: str,
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
            ("status", status),
            ("project_id", project_id),
            ("created_by", created_by),
        ]:
            if not param_value or not str(param_value).strip():
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Missing required parameter: '{param_name}'",
                    }
                )

        title_str = str(title).strip()
        status_str = str(status).strip().lower()
        project_id_str = str(project_id).strip()
        created_by_str = str(created_by).strip()

        if status_str != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Invalid status '{status_str}'. "
                        f"Must be 'active'"
                    ),
                }
            )

        documents_dict = data.get("documents", {})
        projects_dict = data.get("projects", {})
        users_dict = data.get("users", {})

        if project_id_str not in projects_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Project with ID '{project_id_str}' not found",
                }
            )

        project = projects_dict[project_id_str]
        if not isinstance(project, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Invalid project data structure for ID '{project_id_str}'"
                    ),
                }
            )

        if created_by_str not in users_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with ID '{created_by_str}' not found (created_by)",
                }
            )

        created_by_user = users_dict[created_by_str]
        if not isinstance(created_by_user, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": (f"Invalid user data structure for ID '{created_by_str}'"),
                }
            )

        user_status = str(created_by_user.get("status", "")).strip().lower()
        if user_status != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"User '{created_by_str}' is not active "
                        f"(status: '{user_status}')"
                    ),
                }
            )

        for doc_id, doc_data in documents_dict.items():
            if not isinstance(doc_data, dict):
                continue
            if (
                str(doc_data.get("project_id", "")).strip() == project_id_str
                and str(doc_data.get("title", "")).strip().lower() == title_str.lower()
            ):
                return json.dumps(
                    {
                        "success": False,
                        "error": (
                            f"A document with the title '{title_str}' already exists "
                            f"in project '{project_id_str}' (document_id: {doc_id})"
                        ),
                    }
                )

        new_document_id = generate_id(documents_dict)

        new_document = {
            "document_id": str(new_document_id),
            "title": str(title_str),
            "status": str(status_str),
            "project_id": str(project_id_str),
            "created_by": str(created_by_str),
            "body": None,
            "created_at": timestamp,
            "updated_at": timestamp,
            "updated_by": str(created_by_str),
        }

        documents_dict[new_document_id] = new_document

        return json.dumps(
            {
                "success": True,
                "document": new_document,
                "message": (
                    f"Document '{title_str}' created successfully "
                    f"with ID '{new_document_id}' for project '{project_id_str}'"
                ),
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_document",
                "description": "Creates a new empty project document to serve as the single source of truth for a project. "
                    "Use this during project setup to initialise the project brief, or during project kickoff when no active document exists for the project. "
                    "Document titles must be unique within the same project. ",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the document. ",
                        },
                        "status": {
                            "type": "string",
                            "description": "The status of the document. ",
                            "enum": ["active"],
                        },
                        "project_id": {
                            "type": "string",
                            "description": "The unique identifier of the project this document belongs to. ",
                        },
                        "created_by": {
                            "type": "string",
                            "description": "The user_id of the user creating the document. ",
                        },
                    },
                    "required": ["title", "status", "project_id", "created_by"],
                },
            },
        }
