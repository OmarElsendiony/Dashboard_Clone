import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpsertComment(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        action: str,
        comment_body: str,
        commentable_type: Optional[str] = None,
        commentable_id: Optional[str] = None,
        comment_id: Optional[str] = None
    ) -> str:
        """
        Create or update a comment.
        - action="create": Requires commentable_type and commentable_id.
        - action="update": Requires comment_id.
        """
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        def get_user_from_token(token: str, tokens_data: Dict[str, Any]) -> Optional[str]:
            """Encode token and find associated user_id"""
            try:
                encoded_token = base64.b64encode(token.encode('utf-8')).decode('utf-8')
                for token_info in tokens_data.values():
                    if token_info.get("token_encoded") == encoded_token:
                        return token_info.get("user_id")
                return None
            except:
                return None
        
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })

        # Validate action
        if action not in ["create", "update"]:
            return json.dumps({
                "success": False,
                "error": f"Invalid action '{action}'. Must be 'create' or 'update'"
            })
        
        comments = data.get("comments", {})
        issues = data.get("issues", {})
        pull_requests = data.get("pull_requests", {})
        repositories = data.get("repositories", {})
        users = data.get("users", {})
        access_tokens = data.get("access_tokens", {})
        repository_collaborators = data.get("repository_collaborators", {})
        organization_members = data.get("organization_members", {})
        
        # Validate access token
        requesting_user_id = get_user_from_token(access_token, access_tokens)
        if not requesting_user_id:
            return json.dumps({
                "success": False,
                "error": "Invalid or expired access token"
            })
            
        author_id = requesting_user_id
        timestamp = "2026-01-01T23:59:00"

        # --- UPDATE LOGIC ---
        if action == "update":
            if not comment_id:
                return json.dumps({
                    "success": False,
                    "error": "comment_id is required for update action"
                })
            
            if comment_id not in comments:
                return json.dumps({
                    "success": False,
                    "error": f"Comment with ID '{comment_id}' not found"
                })
            
            comment = comments[comment_id]
            
            # Security Check: Ownership
            if comment.get("author_id") != author_id:
                return json.dumps({
                    "success": False,
                    "error": "Permission denied. You can only edit your own comments."
                })
                
            comment["comment_body"] = comment_body
            comment["updated_at"] = timestamp
            
            return json.dumps({
                "success": True,
                "action": "update",
                "comment_id": comment_id,
                "comment_data": comment
            })

        # --- CREATE LOGIC ---
        elif action == "create":
            if not commentable_type or not commentable_id:
                return json.dumps({
                    "success": False,
                    "error": "commentable_type and commentable_id are required for create action"
                })

            if commentable_type not in ["issue", "pull_request"]:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid commentable_type '{commentable_type}'"
                })

            # Check if entity exists and get Repository ID
            repository_id = None
            
            if commentable_type == "issue":
                if commentable_id not in issues:
                    return json.dumps({"success": False, "error": f"Issue '{commentable_id}' not found"})
                repository_id = issues[commentable_id].get("repository_id")
            else:
                if commentable_id not in pull_requests:
                    return json.dumps({"success": False, "error": f"Pull Request '{commentable_id}' not found"})
                repository_id = pull_requests[commentable_id].get("repository_id")
            
            # Verify Repository exists
            if repository_id not in repositories:
                 return json.dumps({"success": False, "error": f"Repository '{repository_id}' not found"})
            
            repository = repositories[repository_id]

            # --- PERMISSION CHECK (Read Access) ---
            # To comment, you generally need Read access. 
            has_access = False
            
            # 1. Public repositories
            if repository.get("visibility") == "public":
                has_access = True
            
            # 2. Owner
            if not has_access and repository.get("owner_type") == "user" and repository.get("owner_id") == requesting_user_id:
                has_access = True
                
            # 3. Collaborator
            if not has_access:
                for collab in repository_collaborators.values():
                    if (collab.get("repository_id") == repository_id and
                        collab.get("user_id") == requesting_user_id and
                        collab.get("status") == "active"):
                        has_access = True
                        break
            
            # 4. Organization Member
            if not has_access and repository.get("owner_type") == "organization":
                for membership in organization_members.values():
                    if (membership.get("organization_id") == repository.get("owner_id") and
                        membership.get("user_id") == requesting_user_id and
                        membership.get("status") == "active"):
                        has_access = True
                        break
            
            if not has_access:
                return json.dumps({
                    "success": False,
                    "error": "Insufficient permissions. You do not have access to this repository."
                })
            # --------------------------------------
            
            new_comment_id = generate_id(comments)
            new_comment = {
                "comment_id": new_comment_id,
                "commentable_type": commentable_type,
                "commentable_id": commentable_id,
                "author_id": author_id,
                "comment_body": comment_body,
                "created_at": timestamp,
                "updated_at": timestamp
            }
            comments[new_comment_id] = new_comment
            
            return json.dumps({
                "success": True,
                "action": "create",
                "comment_id": new_comment_id,
                "comment_data": new_comment
            })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "upsert_comment",
                "description": "Create or update a comment. Use action='create' to post a new comment (requires commentable_type/id). Use action='update' to edit an existing comment (requires comment_id). Requires read access to the repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Action to perform. Allowed values: 'create', 'update' (required)"
                        },
                        "access_token": {
                            "type": "string",
                            "description": "Access token for authentication (required)"
                        },
                        "comment_body": {
                            "type": "string",
                            "description": "The text content of the comment (required)"
                        },
                        "commentable_type": {
                            "type": "string",
                            "description": "Type of entity (required for 'create'). Allowed values: 'issue', 'pull_request'"
                        },
                        "commentable_id": {
                            "type": "string",
                            "description": "ID of the issue/PR (required for 'create')"
                        },
                        "comment_id": {
                            "type": "string",
                            "description": "ID of the comment to update (required for 'update')"
                        }
                    },
                    "required": ["action", "access_token", "comment_body"]
                }
            }
        }
