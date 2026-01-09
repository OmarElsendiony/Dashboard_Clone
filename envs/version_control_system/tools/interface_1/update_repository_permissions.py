import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class UpdateRepositoryPermissions(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        repository_id: str,
        user_id: str,
        permission_level: str
    ) -> str:
        """
        Update repository permissions for a user (add/update collaborator).
        """
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        def get_user_from_token(token: str, tokens_data: Dict[str, Any]) -> str:
            """Encode token and find associated user_id"""
            try:
                # Encode token to base64 UTF-8
                encoded_token = base64.b64encode(token.encode('utf-8')).decode('utf-8')
                # Find token in access_tokens by comparing with token_encoded
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
        repository_collaborators = data.get("repository_collaborators", {})
        access_tokens = data.get("access_tokens", {})
        users = data.get("users", {})
        organization_members = data.get("organization_members", {})
        
        # Validate access token and get requesting user_id
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
        
        # Check if target user exists
        if user_id not in users:
            return json.dumps({
                "success": False,
                "error": f"User with ID '{user_id}' not found"
            })
        
        # Correction: Strict validation for permission_level enum
        valid_permissions = ["read", "write", "admin"]
        if permission_level not in valid_permissions:
            return json.dumps({
                "success": False,
                "error": f"Invalid permission_level '{permission_level}'. Must be one of: {', '.join(valid_permissions)}"
            })
        
        repo = repositories[repository_id]
        owner_type = repo.get("owner_type")
        owner_id = repo.get("owner_id")
        
        # Check if requesting user has admin permissions
        has_admin = False
        
        # Check if requesting user is the owner
        if owner_type == "user" and owner_id == requesting_user_id:
            has_admin = True
        
        # Check if requesting user is organization owner
        if owner_type == "organization" and not has_admin:
            for membership in organization_members.values():
                if (membership.get("organization_id") == owner_id and 
                    membership.get("user_id") == requesting_user_id and
                    membership.get("status") == "active" and
                    membership.get("role") == "owner"):
                    has_admin = True
                    break
        
        # Check if requesting user is collaborator with admin permissions
        if not has_admin:
            for collab in repository_collaborators.values():
                if (collab.get("repository_id") == repository_id and
                    collab.get("user_id") == requesting_user_id and
                    collab.get("status") == "active" and
                    collab.get("permission_level") == "admin"):
                    has_admin = True
                    break
        
        if not has_admin:
            return json.dumps({
                "success": False,
                "error": "Insufficient permissions. Only repository admins can manage collaborators"
            })
        
        timestamp = "2026-01-01T23:59:00"
        
        # Check if user is already a collaborator
        existing_collab_id = None
        for collab_id, collab in repository_collaborators.items():
            if (collab.get("repository_id") == repository_id and
                collab.get("user_id") == user_id):
                existing_collab_id = collab_id
                break
        
        # Update existing collaborator
        if existing_collab_id:
            collab = repository_collaborators[existing_collab_id]
            collab["permission_level"] = permission_level
            collab["status"] = "active"
            
            return json.dumps({
                "success": True,
                "action": "update",
                "repository_id": repository_id,
                "user_id": user_id,
                "permission_level": permission_level,
                "collaborator_id": existing_collab_id,
                "collaborator_data": collab
            })
        
        # Add new collaborator
        else:
            new_collab_id = generate_id(repository_collaborators)
            new_collab = {
                "collaborator_id": new_collab_id,
                "repository_id": repository_id,
                "user_id": user_id,
                "permission_level": permission_level,
                "status": "active",
                "added_at": timestamp
            }
            
            repository_collaborators[new_collab_id] = new_collab
            
            return json.dumps({
                "success": True,
                "action": "create",
                "repository_id": repository_id,
                "user_id": user_id,
                "permission_level": permission_level,
                "collaborator_id": new_collab_id,
                "collaborator_data": new_collab
            })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_repository_permissions",
                "description": "Update repository permissions for a user (add or update collaborator). Requires admin permissions on the repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "Access token for authentication (required)"
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Repository ID to update permissions for (required)"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User ID to grant/update permissions for (required)"
                        },
                        "permission_level": {
                            "type": "string",
                            "description": "Permission level to grant. Allowed values: 'read', 'write', 'admin' (required)"
                        }
                    },
                    "required": ["access_token", "repository_id", "user_id", "permission_level"]
                }
            }
        }