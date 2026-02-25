import json
from typing import Any, Dict, Optional

from tau_bench.envs.tool import Tool


class ManageDocument(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        document_id: Optional[str] = None,
        title: Optional[str] = None,
        body: Optional[str] = None,
        project_id: Optional[str] = None,
        incident_id: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-11T23:59:00"

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        action_str = str(action).strip().lower()
        valid_actions = ["create", "update", "delete"]
        if action_str not in valid_actions:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid action '{action_str}'. Valid values: {', '.join(valid_actions)}",
                }
            )

        documents = data.get("documents", {})
        projects = data.get("projects", {})
        incidents = data.get("incidents", {})

        if action_str == "create":
            if document_id is not None:
                return json.dumps(
                    {
                        "success": False,
                        "error": "document_id should not be provided when creating a document",
                    }
                )

            if not all([title, project_id]):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Create requires: title, project_id",
                    }
                )

            title_str = str(title).strip()
            pid = str(project_id).strip()

            # Validate project exists and status is open/in_progress
            project = projects.get(pid)
            if project is None:
                return json.dumps({"success": False, "error": f"Project '{pid}' not found"})
            if str(project.get("status", "")) not in ["open", "in_progress"]:
                return json.dumps({"success": False, "error": f"Project '{pid}' is not active. Current status: {str(project.get('status', ''))}"})

            # Duplicate title check within project
            for doc in documents.values():
                if str(doc.get("project_id", "")) == pid and str(doc.get("title", "")).lower() == title_str.lower():
                    return json.dumps(
                        {
                            "success": False,
                            "error": f"Document with title '{title_str}' already exists in project '{pid}'",
                        }
                    )

            # Validate incident_id if provided
            if incident_id is not None:
                iid = str(incident_id).strip()
                if iid not in incidents:
                    return json.dumps({"success": False, "error": f"Incident '{iid}' not found"})
                # Validate incident belongs to project
                if str(incidents[iid].get("project_id", "")) != pid:
                    return json.dumps({"success": False, "error": f"Incident '{iid}' does not belong to project '{pid}'"})

            if documents:
                max_id = max(int(k) for k in documents.keys())
                new_id = str(max_id + 1)
            else:
                new_id = "1"

            new_doc = {
                "document_id": new_id,
                "title": title_str,
                "body": str(body).strip() if body else None,
                "project_id": pid,
                "incident_id": str(incident_id).strip() if incident_id else None,
                "created_at": timestamp,
                "updated_at": timestamp,
            }

            documents[new_id] = new_doc

            response = {
                "document_id": str(new_doc.get("document_id", "")),
                "title": str(new_doc.get("title", "")),
                "body": str(new_doc.get("body", "")) if new_doc.get("body") else None,
                "project_id": str(new_doc.get("project_id", "")),
                "incident_id": str(new_doc.get("incident_id", "")) if new_doc.get("incident_id") else None,
                "created_at": str(new_doc.get("created_at", "")),
                "updated_at": str(new_doc.get("updated_at", "")),
            }
            return json.dumps({"success": True, "document": response})

        elif action_str == "update":
            if not document_id:
                return json.dumps(
                    {"success": False, "error": "Update requires: document_id"}
                )

            did = str(document_id).strip()
            doc = documents.get(did)
            if doc is None:
                return json.dumps(
                    {"success": False, "error": f"Document '{did}' not found"}
                )

            if not any([title, body, project_id, incident_id]):
                return json.dumps(
                    {
                        "success": False,
                        "error": "At least one field to update must be provided",
                    }
                )

            # Determine the effective project for validation
            if project_id is not None:
                target_pid = str(project_id).strip()
                project = projects.get(target_pid)
                if project is None:
                    return json.dumps({"success": False, "error": f"Project '{target_pid}' not found"})
                if str(project.get("status", "")) not in ["open", "in_progress"]:
                    return json.dumps({"success": False, "error": f"Project '{target_pid}' is not active. Current status: {str(project.get('status', ''))}"})
            else:
                target_pid = str(doc.get("project_id", ""))

            # Duplicate title check in target project
            if title is not None or project_id is not None:
                check_title = str(title).strip() if title is not None else str(doc.get("title", ""))
                for other_doc in documents.values():
                    if other_doc.get("document_id") == doc.get("document_id"):
                        continue
                    if (str(other_doc.get("project_id", "")) == target_pid
                            and str(other_doc.get("title", "")).lower() == check_title.lower()):
                        return json.dumps(
                            {
                                "success": False,
                                "error": f"Document with title '{check_title}' already exists in project '{target_pid}'",
                            }
                        )

            # Validate incident_id if provided
            if incident_id is not None:
                iid = str(incident_id).strip()
                if iid not in incidents:
                    return json.dumps({"success": False, "error": f"Incident '{iid}' not found"})
                if str(incidents[iid].get("project_id", "")) != target_pid:
                    return json.dumps({"success": False, "error": f"Incident '{iid}' does not belong to project '{target_pid}'"})

            if title is not None:
                doc["title"] = str(title).strip()

            if body is not None:
                doc["body"] = str(body).strip()

            if project_id is not None:
                doc["project_id"] = target_pid

            if incident_id is not None:
                doc["incident_id"] = str(incident_id).strip()

            doc["updated_at"] = timestamp

            response = {
                "document_id": str(doc.get("document_id", "")),
                "title": str(doc.get("title", "")),
                "body": str(doc.get("body", "")) if doc.get("body") else None,
                "project_id": str(doc.get("project_id", "")) if doc.get("project_id") else None,
                "incident_id": str(doc.get("incident_id", "")) if doc.get("incident_id") else None,
                "created_at": str(doc.get("created_at", "")),
                "updated_at": str(doc.get("updated_at", "")),
            }
            return json.dumps({"success": True, "document": response})

        elif action_str == "delete":
            if not document_id:
                return json.dumps(
                    {"success": False, "error": "Delete requires: document_id"}
                )

            did = str(document_id).strip()
            if did not in documents:
                return json.dumps(
                    {"success": False, "error": f"Document '{did}' not found"}
                )

            deleted_doc = documents.pop(did)
            return json.dumps(
                {
                    "success": True,
                    "message": f"Document '{str(deleted_doc.get('title', ''))}' has been deleted",
                }
            )

        return json.dumps({"success": False, "error": "Unexpected error"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "manage_document",
                "description": "Manages document lifecycle by creating, updating, or deleting document records.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "The action to perform",
                            "enum": ["create", "update", "delete"],
                        },
                        "document_id": {
                            "type": "string",
                            "description": "Unique document identifier.",
                        },
                        "title": {
                            "type": "string",
                            "description": "Document title",
                        },
                        "body": {
                            "type": "string",
                            "description": "Document body content",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier (project_id).",
                        },
                        "incident_id": {
                            "type": "string",
                            "description": "Incident identifier (incident_id).",
                        },
                    },
                    "required": ["action"],
                    "allOf": [
                        {
                            "if": {
                                "properties": {"action": {"enum": ["create"]}}
                            },
                            "then": {
                                "required": ["title", "project_id"]
                            },
                        },
                        {
                            "if": {
                                "properties": {"action": {"enum": ["update"]}}
                            },
                            "then": {
                                "required": ["document_id"],
                                "anyOf": [
                                    {"required": ["title"]},
                                    {"required": ["body"]},
                                    {"required": ["project_id"]},
                                    {"required": ["incident_id"]},
                                ],
                            },
                        },
                        {
                            "if": {
                                "properties": {"action": {"enum": ["delete"]}}
                            },
                            "then": {
                                "required": ["document_id"]
                            },
                        },
                    ],
                },
            },
        }
