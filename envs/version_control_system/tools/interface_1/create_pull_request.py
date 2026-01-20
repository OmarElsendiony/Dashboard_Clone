import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreatePullRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        repository_id: str,
        title: str,
        source_branch: str,
        target_branch: str,
        description: Optional[str] = None,
        status: Optional[str] = None
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
        
        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        pull_requests = data.get("pull_requests", {})
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
        
        # Author is always the authenticated user
        author_id = requesting_user_id
        
        # Check if repository exists
        if repository_id not in repositories:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repository_id}' not found"
            })
        
        # Check if author exists (should always be true since we got it from token)
        if author_id not in users:
            return json.dumps({
                "success": False,
                "error": f"Authenticated user with ID '{author_id}' not found"
            })
        
        repository = repositories[repository_id]
        owner_id = repository.get("owner_id")
        owner_type = repository.get("owner_type")
        
        # Validate source branch exists
        source_branch_exists = False
        for branch in branches.values():
            if (branch.get("repository_id") == repository_id and 
                branch.get("branch_name") == source_branch):
                source_branch_exists = True
                break
        
        if not source_branch_exists:
            return json.dumps({
                "success": False,
                "error": f"Source branch '{source_branch}' not found in repository"
            })
        
        # Validate target branch exists
        target_branch_exists = False
        for branch in branches.values():
            if (branch.get("repository_id") == repository_id and 
                branch.get("branch_name") == target_branch):
                target_branch_exists = True
                break
        
        if not target_branch_exists:
            return json.dumps({
                "success": False,
                "error": f"Target branch '{target_branch}' not found in repository"
            })
        
        # Validate source and target branches are different
        if source_branch == target_branch:
            return json.dumps({
                "success": False,
                "error": "Source and target branches must be different"
            })
        
        # Check if user has permission to create pull requests
        has_permission = False
        
        # Check if user is the owner
        if owner_type == "user" and owner_id == requesting_user_id:
            has_permission = True
        
        # Check if user is a collaborator with write or admin access
        if not has_permission:
            for collab in repository_collaborators.values():
                if (collab.get("repository_id") == repository_id and
                    collab.get("user_id") == requesting_user_id and
                    collab.get("permission_level") in ["write", "admin"] and
                    collab.get("status") == "active"):
                    has_permission = True
                    break
        
        # Check if repository is owned by an organization and user is a member
        if not has_permission and owner_type == "organization":
            for membership in organization_members.values():
                if (membership.get("organization_id") == owner_id and
                    membership.get("user_id") == requesting_user_id and
                    membership.get("status") == "active"):
                    has_permission = True
                    break
        
        if not has_permission:
            return json.dumps({
                "success": False,
                "error": "Insufficient permissions. You must have write access to this repository to create pull requests"
            })
        
        # Validate status if provided
        if status and status not in ["open", "closed", "merged", "draft"]:
            return json.dumps({
                "success": False,
                "error": f"Invalid status '{status}'. Must be 'open', 'closed', 'merged', or 'draft'"
            })
        
        # Generate pull request number (sequential per repository)
        pr_number = 1
        for pr in pull_requests.values():
            if pr.get("repository_id") == repository_id:
                current_number = pr.get("pull_request_number", 0)
                if current_number >= pr_number:
                    pr_number = current_number + 1
        
        timestamp = "2026-01-01T23:59:00"
        new_pr_id = generate_id(pull_requests)
        
        new_pr = {
            "pull_request_id": new_pr_id,
            "repository_id": repository_id,
            "pull_request_number": pr_number,
            "title": title,
            "description": description,
            "author_id": author_id,
            "source_branch": source_branch,
            "target_branch": target_branch,
            "status": status if status else "open",
            "merged_by": None,
            "merged_at": None,
            "closed_at": None,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        pull_requests[new_pr_id] = new_pr
        
        return json.dumps({
            "success": True,
            "pull_request_id": new_pr_id,
            "pull_request_data": new_pr
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_pull_request",
                "description": "Creates a new pull request in a repository. The author is automatically set to the authenticated user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "Access token for authentication (required)"
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Repository ID (required)"
                        },
                        "title": {
                            "type": "string",
                            "description": "Pull request title (required)"
                        },
                        "source_branch": {
                            "type": "string",
                            "description": "Source branch name (required)"
                        },
                        "target_branch": {
                            "type": "string",
                            "description": "Target branch name (required)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Pull request description (optional)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Pull request status. Allowed values: 'open', 'closed', 'merged', 'draft' (optional, defaults to 'open')",
                            "enum": ["open", "closed", "merged", "draft"]
                        }
                    },
                    "required": ["access_token", "repository_id", "title", "source_branch", "target_branch"]
                }
            }
        }
