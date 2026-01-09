import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateBranch(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        repository_id: str,
        branch_name: str,
        source_branch: Optional[str] = None
    ) -> str:
        """
        Create a new branch in a repository.
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
                "error": "Cannot create branches in an archived repository"
            })
        
        owner_id = repository.get("owner_id")
        owner_type = repository.get("owner_type")
        
        # Check if user has permission to create branches
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
                "error": "Insufficient permissions. You must have write access to this repository to create branches"
            })
        
        # Check if branch name already exists in this repository
        for branch in branches.values():
            if (branch.get("repository_id") == repository_id and
                branch.get("branch_name") == branch_name):
                return json.dumps({
                    "success": False,
                    "error": f"Branch '{branch_name}' already exists in this repository"
                })
        
        # Find source branch if provided
        source_branch_id = None
        source_commit_sha = None
        
        if source_branch:
            for branch_id, branch in branches.items():
                if (branch.get("repository_id") == repository_id and
                    branch.get("branch_name") == source_branch):
                    source_branch_id = branch_id
                    source_commit_sha = branch.get("commit_sha")
                    break
            
            if not source_branch_id:
                return json.dumps({
                    "success": False,
                    "error": f"Source branch '{source_branch}' not found in this repository"
                })
        else:
            # Try to find default branch as source
            for branch_id, branch in branches.items():
                if (branch.get("repository_id") == repository_id and
                    branch.get("is_default") == True):
                    source_branch_id = branch_id
                    source_commit_sha = branch.get("commit_sha")
                    break
            
            # If no default branch exists, this is the first branch
            # (source_branch_id and source_commit_sha remain None)
        
        timestamp = "2026-01-01T23:59:00"
        new_branch_id = generate_id(branches)
        
        new_branch = {
            "branch_id": new_branch_id,
            "repository_id": repository_id,
            "branch_name": branch_name,
            "commit_sha": source_commit_sha,
            "source_branch": source_branch_id,
            "is_default": False,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        branches[new_branch_id] = new_branch
        
        return json.dumps({
            "success": True,
            "branch_id": new_branch_id,
            "branch_data": new_branch
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_branch",
                "description": "Create a new branch in a repository. If source_branch is provided, the new branch will be created from that branch; otherwise, it will be created from the default branch. If no default branch exists, this will be the first branch. Requires write or admin access to the repository. Cannot create branches in archived repositories.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "Access token for authentication (required)"
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Repository ID to create the branch in (required)"
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "Name of the new branch (required)"
                        },
                        "source_branch": {
                            "type": "string",
                            "description": "Name of the source branch to create from (optional, defaults to default branch if it exists)"
                        }
                    },
                    "required": ["access_token", "repository_id", "branch_name"]
                }
            }
        }