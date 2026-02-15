import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ManageKbPage(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        page_id: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[str] = None,
        space_key: Optional[str] = None,
        status: Optional[str] = None,
        related_ticket_id: Optional[str] = None,
        source_page_id: Optional[str] = None,
    ) -> str:
        if not action:
            return json.dumps({"success": False, "error": "Missing Argument: 'action' is required."})

        def _format_page(db_obj: Dict) -> Dict:
            response_obj = db_obj.copy()
            if "document_id" in response_obj:
                response_obj["page_id"] = response_obj.pop("document_id")
            return response_obj

        def _generate_new_id(pages_db: Dict) -> str:
            if not pages_db:
                return "1"
            try:
                numeric_ids = [int(k) for k in pages_db.keys() if k.isdigit()]
                return str(max(numeric_ids) + 1) if numeric_ids else "1"
            except (ValueError, TypeError):
                return str(len(pages_db) + 1)

        def _find_page_by_id(pages_db: Dict, page_id: str) -> Optional[Dict]:
            return pages_db.get(str(page_id))

        def _check_duplicate(pages_db: Dict, title: str, space_key: str, exclude_id: Optional[str] = None) -> Optional[str]:
            for pid, page in pages_db.items():
                if (
                    page.get("title") == title
                    and page.get("space_key") == space_key
                    and page.get("status") != "Archived"
                    and str(pid) != str(exclude_id)
                ):
                    return page.get("document_id", pid)
            return None

        VALID_ACTIONS = ["create", "update", "move", "copy", "archive"]
        VALID_SPACES = ["Drafts_Space", "Public_KB_Space"]
        VALID_STATUSES = ["WIP", "Verified", "Archived"]

        try:
            if not isinstance(data, dict):
                return json.dumps({"success": False, "error": "Invalid data format"})

            if "documents" not in data:
                data["documents"] = {}
            pages_db = data["documents"]

            timestamp = "2026-02-02T23:59:00"

            if action not in VALID_ACTIONS:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid Argument: action must be one of {VALID_ACTIONS}."
                })

            if space_key is not None and space_key not in VALID_SPACES:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid Argument: space_key must be one of {VALID_SPACES}."
                })

            if status is not None and status not in VALID_STATUSES:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid Argument: status must be one of {VALID_STATUSES}."
                })

            if action == "create":
                if not title:
                    return json.dumps({
                        "success": False,
                        "error": "Missing Argument: 'title' is required for create."
                    })

                final_space = space_key if space_key else "Drafts_Space"
                final_status = status if status else "WIP"

                existing_id = _check_duplicate(pages_db, title, final_space)
                if existing_id:
                    return json.dumps({
                        "success": False,
                        "error": f"Duplicate Error: Active page '{title}' already exists in {final_space} (ID: {existing_id})."
                    })

                new_id = _generate_new_id(pages_db)

                new_page = {
                    "document_id": new_id,
                    "title": title,
                    "description": content if content is not None else "",
                    "space_key": final_space,
                    "status": final_status,
                    "related_ticket_id": related_ticket_id,
                    "created_at": timestamp,
                    "updated_at": timestamp
                }

                pages_db[new_id] = new_page

                return json.dumps({
                    "success": True,
                    "page": _format_page(new_page),
                    "message": f"Page '{title}' created successfully in {final_space}."
                })

            if action == "copy":
                if not source_page_id:
                    return json.dumps({
                        "success": False,
                        "error": "Missing Argument: 'source_page_id' is required for copy."
                    })

                source_page = _find_page_by_id(pages_db, source_page_id)
                if not source_page:
                    return json.dumps({
                        "success": False,
                        "error": f"Not Found Error: Source page ID '{source_page_id}' not found."
                    })

                new_title = title if title else f"Copy of {source_page.get('title', 'Untitled')}"
                target_space = space_key if space_key else source_page.get("space_key", "Drafts_Space")

                existing_id = _check_duplicate(pages_db, new_title, target_space)
                if existing_id:
                    return json.dumps({
                        "success": False,
                        "error": f"Duplicate Error: A page with title '{new_title}' already exists in {target_space} (ID: {existing_id})."
                    })

                new_id = _generate_new_id(pages_db)

                new_page = {
                    "document_id": new_id,
                    "title": new_title,
                    "description": source_page.get("description", ""),
                    "space_key": target_space,
                    "status": "WIP",
                    "related_ticket_id": source_page.get("related_ticket_id"),
                    "created_at": timestamp,
                    "updated_at": timestamp
                }

                pages_db[new_id] = new_page

                return json.dumps({
                    "success": True,
                    "page": _format_page(new_page),
                    "message": f"Page copied successfully. New page ID: {new_id}."
                })

            if not page_id:
                return json.dumps({
                    "success": False,
                    "error": f"Missing Argument: 'page_id' is required for {action}."
                })

            target_page = _find_page_by_id(pages_db, page_id)
            if not target_page:
                return json.dumps({
                    "success": False,
                    "error": f"Not Found Error: Page ID '{page_id}' not found."
                })

            if action == "update":
                changes_made = False

                if title is not None and target_page.get("title") != title:
                    current_space = target_page.get("space_key", "Drafts_Space")
                    existing_id = _check_duplicate(pages_db, title, current_space, page_id)
                    if existing_id:
                        return json.dumps({
                            "success": False,
                            "error": f"Duplicate Error: A page with title '{title}' already exists in {current_space} (ID: {existing_id})."
                        })
                    target_page["title"] = title
                    changes_made = True

                if content is not None and target_page.get("description") != content:
                    target_page["description"] = content
                    changes_made = True

                if status is not None and target_page.get("status") != status:
                    target_page["status"] = status
                    changes_made = True

                if related_ticket_id is not None and target_page.get("related_ticket_id") != related_ticket_id:
                    target_page["related_ticket_id"] = related_ticket_id
                    changes_made = True

                if not changes_made:
                    return json.dumps({
                        "success": False,
                        "error": "No changes detected. The page already has these values."
                    })

                target_page["updated_at"] = timestamp

                return json.dumps({
                    "success": True,
                    "page": _format_page(target_page),
                    "message": f"Page '{target_page.get('title')}' updated successfully."
                })

            if action == "move":
                if not space_key:
                    return json.dumps({
                        "success": False,
                        "error": "Missing Argument: 'space_key' is required for move."
                    })

                current_space = target_page.get("space_key")
                if current_space == space_key:
                    return json.dumps({
                        "success": False,
                        "error": f"Page is already in space '{space_key}'."
                    })

                page_title = target_page.get("title", "")
                existing_id = _check_duplicate(pages_db, page_title, space_key, page_id)
                if existing_id:
                    return json.dumps({
                        "success": False,
                        "error": f"Duplicate Error: A page with title '{page_title}' already exists in {space_key} (ID: {existing_id})."
                    })

                target_page["space_key"] = space_key
                target_page["updated_at"] = timestamp

                return json.dumps({
                    "success": True,
                    "page": _format_page(target_page),
                    "message": f"Page moved from '{current_space}' to '{space_key}'."
                })

            if action == "archive":
                if target_page.get("status") == "Archived":
                    return json.dumps({
                        "success": False,
                        "error": "Page is already archived."
                    })

                target_page["status"] = "Archived"
                target_page["updated_at"] = timestamp

                return json.dumps({
                    "success": True,
                    "page": _format_page(target_page),
                    "message": f"Page '{target_page.get('title')}' archived successfully."
                })

            return json.dumps({"success": False, "error": "Unknown action."})

        except Exception as e:
            return json.dumps({"success": False, "error": f"System Error: {str(e)}"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "manage_kb_page",
                "description": (
                    "A comprehensive lifecycle management tool for Knowledge Base (KB) pages. "
                    "Handles creating new pages, updating existing content, moving pages between spaces "
                    "(e.g., Drafts to Public), copying pages, and archiving (soft-deleting) obsolete content.\n\n"
                    "CAPABILITIES:\n"
                    "1. CREATE: Creates new pages. Enforces uniqueness (Title + Space) to prevent duplicates. "
                    "Defaults to 'Drafts_Space' and 'WIP' status. Stores body text in 'description' field.\n"
                    "2. UPDATE: Modifies existing pages (title, content, status, related_ticket_id). "
                    "Enforces idempotency - fails if no values actually change.\n"
                    "3. MOVE: Transfers a page between spaces (e.g., Drafts -> Public). "
                    "Validates no duplicate exists in target space.\n"
                    "4. COPY: Duplicates a page using 'source_page_id'. Allows renaming and retargeting to a new space.\n"
                    "5. ARCHIVE: Soft-deletes a page by setting status to 'Archived'.\n\n"
                    "NOTE: Internally maps 'document_id' to 'page_id' and 'content' input to 'description' storage."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["create", "update", "move", "copy", "archive"],
                            "description": "REQUIRED. The lifecycle operation to perform on the KB page."
                        },
                        "page_id": {
                            "type": "string",
                            "description": (
                                "CONDITIONAL. The unique ID of the target page. "
                                "Required for 'update', 'move', and 'archive' actions."
                            )
                        },
                        "title": {
                            "type": "string",
                            "description": (
                                "CONDITIONAL. The page title. Required for 'create'. "
                                "Optional for 'update' (to rename) or 'copy' (to override source title)."
                            )
                        },
                        "content": {
                            "type": "string",
                            "description": (
                                "OPTIONAL. The main body text of the page. "
                                "Mapped to the 'description' field in the database."
                            )
                        },
                        "space_key": {
                            "type": "string",
                            "enum": ["Drafts_Space", "Public_KB_Space"],
                            "description": (
                                "CONDITIONAL. The destination workspace. Required for 'move'. "
                                "Optional for 'create' (defaults to 'Drafts_Space') and 'copy'."
                            )
                        },
                        "status": {
                            "type": "string",
                            "enum": ["WIP", "Verified", "Archived"],
                            "description": (
                                "OPTIONAL. The publication state. Defaults to 'WIP' on creation. "
                                "Use 'update' to change status, or 'archive' action for soft-delete."
                            )
                        },
                        "related_ticket_id": {
                            "type": "string",
                            "description": (
                                "OPTIONAL. Links the page to a specific Support Ticket ID "
                                "for audit traceability and context."
                            )
                        },
                        "source_page_id": {
                            "type": "string",
                            "description": (
                                "CONDITIONAL. The ID of the original page to duplicate. "
                                "Required only for the 'copy' action."
                            )
                        }
                    },
                    "required": ["action"]
                }
            }
        }
