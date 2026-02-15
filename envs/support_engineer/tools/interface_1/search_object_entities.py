import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class SearchObjectEntities(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        object_type: str,
        id: Optional[str] = None,
        query: Optional[str] = None,
        tag_name: Optional[str] = None,
        tag_type: Optional[str] = None,
        page_name: Optional[str] = None,
        limit: int = 20,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not object_type:
            return json.dumps({"success": False, "error": "Missing Argument: 'object_type' is required."})

        type_map = {
            "repository": "repositories",
            "channel": "channels",
            "channel_member": "channel_members",
            "pull_request": "pull_requests",
            "branch": "branches",
            "file": "files",
            "message": "channel_messages",
            "ticket": "tickets",
            "issue": "issues",
            "note": "ticket_notes",
            "comment": "ticket_comments",
            "tag": "tags",
            "ticket_tag": "ticket_tags",
            "page": "documents"
        }

        if object_type not in type_map:
            return json.dumps({
                "success": False,
                "error": f"Invalid Argument: object_type must be one of {list(type_map.keys())}."
            })

        collection_key = type_map[object_type]
        collection = data.get(collection_key, {})

        results = []

        for key, item in collection.items():
            match = True

            if id:
                id_match_found = False

                if object_type == "ticket" and str(item.get("ticket_id")) == str(id):
                    id_match_found = True
                elif object_type == "note" and str(item.get("note_id")) == str(id):
                    id_match_found = True
                elif object_type == "comment" and str(item.get("comment_id")) == str(id):
                    id_match_found = True
                elif object_type == "tag" and str(item.get("tag_id")) == str(id):
                    id_match_found = True
                elif object_type == "issue" and str(item.get("issue_id")) == str(id):
                    id_match_found = True
                elif object_type == "page" and str(item.get("document_id")) == str(id):
                    id_match_found = True
                elif object_type == "channel" and str(item.get("channel_id")) == str(id):
                    id_match_found = True
                elif object_type == "ticket_tag" and str(item.get("tag_id")) == str(id):
                    id_match_found = True
                elif object_type == "channel_member" and str(item.get("user_id")) == str(id):
                    id_match_found = True
                elif object_type != "ticket_tag" and object_type != "channel_member" and str(item.get("id", key)) == str(id):
                    id_match_found = True

                if not id_match_found:
                    match = False

            if tag_name and item.get("tag_name") != tag_name:
                match = False
            if tag_type and item.get("tag_type") != tag_type:
                match = False

            if page_name and match:
                val = item.get("doc_name")
                if val:
                    try:
                        pattern = re.compile(page_name, re.IGNORECASE)
                        if not pattern.search(val):
                            match = False
                    except re.error:
                        return json.dumps({"success": False, "error": "Invalid Regex Pattern for page_name."})
                else:
                    match = False

            if query and match:
                text_match = False
                try:
                    pattern = re.compile(query, re.IGNORECASE)
                except re.error:
                    return json.dumps({"success": False, "error": "Invalid Regex Pattern."})

                for val in item.values():
                    if isinstance(val, str) and pattern.search(val):
                        text_match = True
                        break

                if not text_match:
                    match = False

            if match:
                result_item = item.copy()

                if object_type == "page":
                    if "document_id" in result_item:
                        result_item["page_id"] = result_item.pop("document_id")
                    if "doc_name" in result_item:
                        result_item["page_name"] = result_item.pop("doc_name")

                results.append(result_item)

        if object_type == "ticket":
            ticket_tags_link = data.get("ticket_tags", {})
            all_notes = data.get("ticket_notes", {})
            all_docs = data.get("documents", {})

            for ticket in results:
                t_id = str(ticket.get("ticket_id")).strip()

                found_tag_ids = []
                for link in ticket_tags_link.values():
                    if str(link.get("ticket_id")).strip() == t_id:
                        found_tag_ids.append(link.get("tag_id"))
                ticket["tag_ids"] = found_tag_ids

                related_notes = []
                for note in all_notes.values():
                    if str(note.get("ticket_id")).strip() == t_id:
                        related_notes.append(note)
                ticket["related_notes"] = related_notes

                related_pages = []
                for doc in all_docs.values():
                    link_id = doc.get("related_ticket_id")
                    if link_id and str(link_id).strip() == t_id:
                        page_obj = doc.copy()
                        if "document_id" in page_obj:
                            page_obj["page_id"] = page_obj.pop("document_id")
                        if "doc_name" in page_obj:
                            page_obj["page_name"] = page_obj.pop("doc_name")
                        related_pages.append(page_obj)

                ticket["related_pages"] = related_pages

        if object_type == "channel":
            all_members = data.get("channel_members", {})

            for channel in results:
                c_id = str(channel.get("channel_id")).strip()
                member_ids = []

                for member_record in all_members.values():
                    if str(member_record.get("channel_id")).strip() == c_id:
                        user_id = member_record.get("user_id")
                        if user_id:
                            member_ids.append(str(user_id))

                channel["member_ids"] = member_ids

        limit_val = limit if isinstance(limit, int) and limit > 0 else 20
        truncated = False
        if len(results) > limit_val:
            results = results[:limit_val]
            truncated = True

        return json.dumps({
            "success": True,
            "object_type": object_type,
            "count": len(results),
            "results": results,
            "truncated": truncated
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "search_object_entities",
                "description": (
                    "Smart database search for retrieving entities and their relationships.\n"
                    "PURPOSE: To find specific records using IDs, text regex, or specific attributes.\n"
                    "WHEN TO USE: Use this to find a Ticket's linked Notes/Tags/Pages, search for Pages by name/content, or browse entities like Pull Requests, Branches,\n"
                    "Files, Messages, Issues, Comments , Channel members and Tags. \n"
                    "RETURNS: A list of matching objects. 'tickets' are enriched with 'tag_ids', 'related_notes', and 'related_pages'. 'channels' are enriched with 'member_ids'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "object_type": {
                            "type": "string",
                            "enum": [
                                "repository", "channel", "channel_member", "pull_request", "branch",
                                "file", "message", "ticket", "issue",
                                "note", "comment", "tag", "ticket_tag", "page"
                            ],
                            "description": "REQUIRED. The category of object to search."
                        },
                        "id": {
                            "type": "string",
                            "description": "Optional. Exact ID to search for (e.g., '105', 'note_55', 'doc_1'). For 'channel_member', matches user_id only."
                        },
                        "query": {
                            "type": "string",
                            "description": "Optional. Text or Regex to search for in ANY field (e.g., page title)."
                        },
                        "tag_name": {
                            "type": "string",
                            "description": "Optional. Specific name for tags."
                        },
                        "tag_type": {
                            "type": "string",
                            "description": "Optional. Specific type for tags."
                        },
                        "page_name": {
                            "type": "string",
                            "description": "Optional. Partial name search (Regex) for pages (KB articles)."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Optional. Max results (default 20)."
                        }
                    },
                    "required": ["object_type"]
                }
            }
        }
