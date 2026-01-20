import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class SubmitPrReview(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        pull_request_id: str,
        review_state: str,
        review_body: Optional[str] = None
    ) -> str:
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
        
        # Validate review_state
        if review_state not in ["pending", "approved", "changes_requested", "commented", "dismissed"]:
            return json.dumps({
                "success": False,
                "error": f"Invalid review_state '{review_state}'"
            })
        
        repositories = data.get("repositories", {})
        pull_requests = data.get("pull_requests", {})
        pull_request_reviews = data.get("pull_request_reviews", {})
        users = data.get("users", {})
        access_tokens = data.get("access_tokens", {})
        repository_collaborators = data.get("repository_collaborators", {})
        organization_members = data.get("organization_members", {})
        
        # Validate access token AND get Reviewer ID
        requesting_user_id = get_user_from_token(access_token, access_tokens)
        if not requesting_user_id:
            return json.dumps({
                "success": False,
                "error": "Invalid or expired access token"
            })
            
        reviewer_id = requesting_user_id
        
        # Check if pull request exists
        if pull_request_id not in pull_requests:
            return json.dumps({
                "success": False,
                "error": f"Pull request with ID '{pull_request_id}' not found"
            })
            
        pull_request = pull_requests[pull_request_id]
        repository_id = pull_request.get("repository_id")
        
        # Check if repository exists
        if repository_id not in repositories:
             return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repository_id}' not found"
            })
            
        repository = repositories[repository_id]
        
        # --- PERMISSION CHECK (Read Access) ---
        # User needs at least READ access to review a PR
        has_access = False
        
        # 1. Public repositories are accessible to everyone
        if repository.get("visibility") == "public":
            has_access = True
            
        # 2. Check if user is the Owner
        if not has_access:
            if repository.get("owner_type") == "user" and repository.get("owner_id") == requesting_user_id:
                has_access = True
                
        # 3. Check if user is a Collaborator (Read, Write, or Admin)
        if not has_access:
            for collab in repository_collaborators.values():
                if (collab.get("repository_id") == repository_id and
                    collab.get("user_id") == requesting_user_id and
                    collab.get("status") == "active"):
                    # Any permission level (read/write/admin) allows viewing/reviewing
                    has_access = True
                    break
        
        # 4. Check if user is an Organization Member
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

        # Prevent Self-Review
        if pull_request.get("author_id") == reviewer_id:
             return json.dumps({
                "success": False,
                "error": "You cannot review your own pull request."
            })

        timestamp = "2026-01-01T23:59:00"
        new_review_id = generate_id(pull_request_reviews)
        
        new_review = {
            "review_id": new_review_id,
            "pull_request_id": pull_request_id,
            "reviewer_id": reviewer_id,
            "review_state": review_state,
            "review_body": review_body,
            "submitted_at": timestamp,
            "created_at": timestamp
        }
        
        pull_request_reviews[new_review_id] = new_review
        
        return json.dumps({
            "success": True,
            "review_id": new_review_id,
            "review_data": new_review
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "submit_pr_review",
                "description": "Submits a review for a pull request.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "Access token for authentication (required)"
                        },
                        "pull_request_id": {
                            "type": "string",
                            "description": "Pull request ID (required)"
                        },
                        "review_state": {
                            "type": "string",
                            "description": "Review state. Allowed values: 'pending', 'approved', 'changes_requested', 'commented', 'dismissed' (required)",
                            "enum": ["pending", "approved", "changes_requested", "commented", "dismissed"]
                        },
                        "review_body": {
                            "type": "string",
                            "description": "Review body text (optional)"
                        }
                    },
                    "required": ["access_token", "pull_request_id", "review_state"]
                }
            }
        }
