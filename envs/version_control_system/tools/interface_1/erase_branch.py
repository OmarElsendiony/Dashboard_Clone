import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class EraseBranch(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        repository_id: str,
        branch_name: str
    ) -> str:
        """
        Delete a branch from a repository.
        """
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
        
        # Check if repository exists
        if repository_id not in repositories:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repository_id}' not found"
            })
        
        repository = repositories[repository_id]
        
        # Check if repository is archived
        if repository.get("is_archived", False):
            return json.dumps({
                "success": False,
                "error": "Cannot delete branches from an archived repository"
            })
        
        owner_id = repository.get("owner_id")
        owner_type = repository.get("owner_type")
        
        # Check if user has permission to delete branches
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
                "error": "Insufficient permissions. You must have write access to this repository to delete branches"
            })
        
        # Find the branch to delete
        branch_to_delete_id = None
        branch_to_delete = None
        
        for branch_id, branch in branches.items():
            if (branch.get("repository_id") == repository_id and
                branch.get("branch_name") == branch_name):
                branch_to_delete_id = branch_id
                branch_to_delete = branch
                break
        
        if not branch_to_delete_id:
            return json.dumps({
                "success": False,
                "error": f"Branch '{branch_name}' not found in this repository"
            })
        
        # Prevent deletion of default branch
        if branch_to_delete.get("is_default"):
            return json.dumps({
                "success": False,
                "error": f"Cannot delete default branch '{branch_name}'"
            })
        
        # Delete the branch
        del branches[branch_to_delete_id]
        
        return json.dumps({
            "success": True,
            "branch_id": branch_to_delete_id,
            "message": f"Branch '{branch_name}' deleted successfully"
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "erase_branch",
                "description": "Delete a branch from a repository. Cannot delete the default branch. Requires write or admin access to the repository. Cannot delete branches from archived repositories.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "Access token for authentication (will be encoded to base64 UTF-8 and compared with token_encoded) (required)"
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Repository ID to delete the branch from (required)"
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "Name of the branch to delete (required)"
                        }
                    },
                    "required": ["access_token", "repository_id", "branch_name"]
                }
            }
        }