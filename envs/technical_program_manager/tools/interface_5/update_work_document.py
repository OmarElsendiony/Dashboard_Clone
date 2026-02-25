import json
from typing import Any, Dict, List, Optional
from tau_bench.envs.tool import Tool

class UpdateWorkDocument(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any],
               document_identifier: Dict[str, str],
               updated_by: str,
               title: Optional[str] = None,
               status: Optional[str] = None,
               page_updates: Optional[List[Dict[str, Any]]] = None,
               add_pages: Optional[List[Dict[str, Any]]] = None
               ) -> str:
        # 1. Basic data integrity check
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        # System Epoch: 02/11/2026 23:59:00
        now = "2026-02-11T23:59:00"
        documents = data.get("documents", {})
        pages = data.get("pages", {})
        users = data.get("users", {})

        def generate_id(table: Dict[str, Any]) -> str:
            return str(max([int(k) for k in table.keys()], default=0) + 1)

        if not updated_by:
            return json.dumps({"success": False, "error": "updated_by is required."})

        if not any([title, status, page_updates, add_pages]):
             return json.dumps({"success": False, "error": "No updates provided. Include title, status, page_updates, or add_pages."})

        # 2. Advanced Document Identification Logic
        target_doc = None
        d_id = document_identifier.get("document_id")
        d_title = document_identifier.get("title")
        d_project = document_identifier.get("project_id")
        d_incident = document_identifier.get("incident_id")

        if d_id:
            target_doc = documents.get(d_id)
        elif d_title:
            # If project_id is provided, search within that project's scope
            if d_project:
                target_doc = next((d for d in documents.values() if d.get("project_id") == d_project and d_title.lower() in d["title"].lower()), None)
            elif d_incident:
                target_doc = next((d for d in documents.values() if d.get("incident_id") == d_incident and d_title.lower() in d["title"].lower()), None)
            else:
                target_doc = next((d for d in documents.values() if d_title.lower() in d["title"].lower()), None)
        elif d_project or d_incident:
             return json.dumps({"success": False, "error": "project_id or incident_id must be accompanied by a title or partial title to ensure correct document targeting."})

        if not target_doc:
            return json.dumps({"success": False, "error": f"Document not found using criteria: {document_identifier}."})

        if updated_by not in users:
            return json.dumps({"success": False, "error": f"User ID '{updated_by}' not found."})

        document_id = target_doc["document_id"]

        # 3. Handle Document-level updates
        if title:
            target_doc["title"] = title
        if status:
            valid_statuses = ["active", "published", "approved"]
            if status not in valid_statuses:
                return json.dumps({"success": False, "error": f"Invalid status: {status}."})
            target_doc["status"] = status

        target_doc["updated_by"] = updated_by
        target_doc["updated_at"] = now

        # 4. Handle Existing Page Updates
        updated_pages_list = []
        if page_updates:
            doc_pages = [p for p in pages.values() if p["document_id"] == document_id]
            for item in page_updates:
                identifier = item.get("page_identifier", {})
                updates = item.get("new_updates", {})

                target_page = None
                p_id = identifier.get("page_id")
                p_title = identifier.get("title")
                p_keyword = identifier.get("keyword")

                if p_id:
                    target_page = pages.get(p_id)
                elif p_title:
                    target_page = next((p for p in doc_pages if p_title.lower() in p["title"].lower()), None)
                elif p_keyword:
                    target_page = next((p for p in doc_pages if p_keyword.lower() in p["content"].lower()), None)
                else:
                    target_page = doc_pages[0] if doc_pages else None

                if not target_page or target_page["document_id"] != document_id:
                    continue

                if "content" in updates:
                    content = updates["content"]
                    if target_page["type"] == "root_cause_analysis" and "Context:" not in content:
                         return json.dumps({"success": False, "error": "RCA Format Violation: Content must contain 'Context:' and 'Key Decisions:' sections."})
                    target_page["content"] = content

                if "status" in updates:
                    target_page["status"] = updates["status"]

                target_page["updated_at"] = now
                updated_pages_list.append(target_page)

        # 5. Handle New Page Additions
        added_pages_list = []
        if add_pages:
            for new_p_data in add_pages:
                new_page_id = generate_id(pages)
                new_page = {
                    "page_id": new_page_id,
                    "document_id": document_id,
                    "title": new_p_data.get("title", "Untitled Page"),
                    "content": new_p_data.get("content", ""),
                    "type": new_p_data.get("type", "general"),
                    "status": new_p_data.get("status", "draft"),
                    "created_at": now,
                    "updated_at": now
                }

                if new_page["type"] == "root_cause_analysis" and "Context:" not in new_page["content"]:
                     new_page["content"] = "Context: [Draft] | Key Decisions: [Pending] | Stakeholders Involved: [Pending] | Status: Draft"

                pages[new_page_id] = new_page
                added_pages_list.append(new_page)

        return json.dumps({
            "success": True,
            "message": f"Document '{target_doc['title']}' updated.",
            "document": target_doc,
            "updated_pages": [p["page_id"] for p in updated_pages_list],
            "added_pages": [p["page_id"] for p in added_pages_list]
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_work_document",
                "description": "Updates technical documents and their pages. Supports flexible document lookup (document_id, title, project_id, incident_id). Can update document title/status, modify existing pages (content/status), and add new pages. Note: Page updates silently skip if page not found. Enforces RCA content format for root_cause_analysis pages",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_identifier": {
                            "type": "object",
                            "description": "Lookup criteria used to locate the parent document container (e.g., via project_id or formal title).",
                            "properties": {
                                "document_id": {"type": "string", "description": "System ID for the document."},
                                "title": {"type": "string", "description": "Exact formal title of the document."},
                                "project_id": {"type": "string", "description": "Links to the document associated with a specific project."},
                                "incident_id": {"type": "string", "description": "Links to the document associated with a specific incident."}
                            }
                        },
                        "updated_by": {"type": "string", "description": "The user_id of the person making the changes."},
                        "title": {"type": "string", "description": "A new container title if a rename is required."},
                        "status": {
                            "type": "string",
                            "enum": ["active", "published", "approved"],
                            "description": "Updates the lifecycle state of the entire document container."
                        },
                        "page_updates": {
                            "type": "array",
                            "description": "A list of edits for existing pages. Uses a nested identifier (ID, Title, or Keyword) to find the correct page before applying the 'new_updates' payload.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "page_identifier": {
                                        "type": "object",
                                        "description": "Search criteria for the target page.",
                                        "properties": {
                                            "page_id": {"type": "string", "description": "Target by UUID."},
                                            "title": {"type": "string", "description": "Target by exact page title match."},
                                            "keyword": {"type": "string", "description": "Target the first page containing this specific content snippet."}
                                        }
                                    },
                                    "new_updates": {
                                        "type": "object",
                                        "description": "The specific content or status changes to commit.",
                                        "properties": {
                                            "content": {"type": "string", "description": "The revised text body. Must follow RCA format if page type is root_cause_analysis."},
                                            "status": {"type": "string", "enum": ["draft", "approved", "published"], "description": "The revised lifecycle state for the individual page."}
                                        }
                                    }
                                }
                            }
                        },
                        "add_pages": {
                            "type": "array",
                            "description": "A list of new pages to be created and linked to this document. If type is 'root_cause_analysis' and content is missing, a mandatory template is automatically applied.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "The title for the new page record."},
                                    "content": {"type": "string", "description": "The initial text for the new page."},
                                    "type": {
                                        "type": "string",
                                        "enum": ["product_requirement_document", "post_incident_review", "root_cause_analysis", "retrospective", "general"],
                                        "description": "The category of content, used for governance auditing."
                                    },
                                    "status": {"type": "string", "enum": ["draft", "approved", "published"], "description": "The initial lifecycle state of the page."}
                                },
                                "required": ["title"]
                            }
                        }
                    },
                    "required": ["document_identifier", "updated_by"]
                }
            }
        }
