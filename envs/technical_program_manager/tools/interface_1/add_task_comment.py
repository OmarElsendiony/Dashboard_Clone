import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class AddTaskComment(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        work_item_id: str,
        comment_text: str,
        author_id: str
    ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(int(max(table.keys(), key=lambda x: int(x))) + 1)
        
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })
        
        work_items = data.get("work_items", {})
        work_item_comments = data.get("work_item_comments", {})
        users = data.get("users", {})
        
        if not work_item_id or not comment_text or not author_id:
            return json.dumps({
                "success": False,
                "error": "Missing required parameters: work_item_id, comment_text, and author_id are required"
            })
        
        if str(work_item_id) not in work_items:
            return json.dumps({
                "success": False,
                "error": f"Work item with ID '{work_item_id}' not found"
            })
        
        if str(author_id) not in users:
            return json.dumps({
                "success": False,
                "error": f"Author with user_id '{author_id}' not found"
            })
        
        new_comment_id = generate_id(work_item_comments)
        
        new_comment = {
            "comment_id": str(new_comment_id),
            "work_item_id": str(work_item_id),
            "author_id": str(author_id),
            "comment_text": str(comment_text),
            "created_at": "2026-02-11T23:59:00"
        }
        
        work_item_comments[str(new_comment_id)] = new_comment
        
        return json.dumps({
            "success": True,
            "message": "Comment added successfully",
            "comment_id": str(new_comment_id),
            "comment_data": {
                "comment_id": str(new_comment_id),
                "work_item_id": str(work_item_id),
                "author_id": str(author_id),
                "comment_text": str(comment_text),
                "created_at": "2026-02-11T23:59:00"
            }
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_task_comment",
                "description": "Adds a comment to a work item. Use this to document blocker escalations, add status notes, record decisions, communicate updates on specific work items, or provide context for task progress.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "work_item_id": {
                            "type": "string",
                            "description": "The ID of the work item to comment on (required, must exist)"
                        },
                        "comment_text": {
                            "type": "string",
                            "description": "The comment text (required)"
                        },
                        "author_id": {
                            "type": "string",
                            "description": "The ID of the user adding the comment (required, must exist)"
                        }
                    },
                    "required": ["work_item_id", "comment_text", "author_id"]
                }
            }
        }