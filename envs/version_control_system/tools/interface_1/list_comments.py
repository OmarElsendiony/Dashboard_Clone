import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class ListComments(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        commentable_type: str,
        commentable_id: str,
        author_id: str
    ) -> str:
        comments = data.get("comments", {})
        results = []

        valid_types = ['issue', 'pull_request']
        if commentable_type not in valid_types:
            return json.dumps({"error": f"Invalid commentable_type. Must be one of: {', '.join(valid_types)}"})

        for comment in comments.values():
            if (comment.get("commentable_type") == commentable_type and
                comment.get("commentable_id") == commentable_id and
                comment.get("author_id") == author_id):
                results.append(comment)

        return json.dumps(results)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_comments",
                "description": "Lists comments for a specific entity type and ID, authored by a specific user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "commentable_type": {
                            "type": "string",
                            "description": "The type of entity the comment belongs to. Allowed values: 'issue', 'pull_request'.",
                            "enum": ["issue", "pull_request"]
                        },
                        "commentable_id": {
                            "type": "string",
                            "description": "The ID of the entity (issue ID or PR ID)."
                        },
                        "author_id": {
                            "type": "string",
                            "description": "The ID of the author."
                        }
                    },
                    "required": ["commentable_type", "commentable_id", "author_id"]
                }
            }
        }
