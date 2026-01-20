import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetRepositoryPermissions(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        repository_id: str
    ) -> str:
        valid_permissions = {'read', 'write', 'admin'}

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
        organization_members = data.get("organization_members", {})
        
        # Validate access token and get user_id
        user_id = get_user_from_token(access_token, access_tokens)
        if not user_id:
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
        
        repo = repositories[repository_id]
        owner_type = repo.get("owner_type")
        owner_id = repo.get("owner_id")
        
        # Check if user is the owner (Personal Account)
        if owner_type == "user" and owner_id == user_id:
            return json.dumps({
                "success": True,
                "repository_id": repository_id,
                "user_id": user_id,
                "permission_level": "admin",
                "source": "owner"
            })
        
        # Check if user is organization owner/member
        if owner_type == "organization":
            for membership in organization_members.values():
                if (membership.get("organization_id") == owner_id and 
                    membership.get("user_id") == user_id and
                    membership.get("status") == "active"):
                    
                    role = membership.get("role")
                    if role == "owner":
                        return json.dumps({
                            "success": True,
                            "repository_id": repository_id,
                            "user_id": user_id,
                            "permission_level": "admin",
                            "source": "organization_owner"
                        })
                    
                    # Organization members get read by default
                    permission = "read"
                    
                    # Check if they have explicit collaborator permissions that might upgrade them
                    for collab in repository_collaborators.values():
                        if (collab.get("repository_id") == repository_id and
                            collab.get("user_id") == user_id and
                            collab.get("status") == "active"):
                            
                            collab_perm = collab.get("permission_level")
                            if collab_perm in valid_permissions:
                                permission = collab_perm
                            break
                    
                    return json.dumps({
                        "success": True,
                        "repository_id": repository_id,
                        "user_id": user_id,
                        "permission_level": permission,
                        "source": "organization_member"
                    })
        
        # Check if user is a collaborator (for personal repos or non-org-members)
        for collab_id, collab in repository_collaborators.items():
            if (collab.get("repository_id") == repository_id and
                collab.get("user_id") == user_id and
                collab.get("status") == "active"):
                
                perm = collab.get("permission_level")
                
                # Correction: Strictly validate the permission level against allowed enum
                if perm in valid_permissions:
                    return json.dumps({
                        "success": True,
                        "repository_id": repository_id,
                        "user_id": user_id,
                        "permission_level": perm,
                        "source": "collaborator",
                        "collaborator_id": collab_id
                    })
        
        # Correction: If no valid permission is found, return False/Error 
        # instead of returning "no permission" which violates the enum schema.
        return json.dumps({
            "success": False,
            "error": "User does not have read, write, or admin access to this repository"
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_repository_permissions",
                "description": "Gets repository permissions for the authenticated user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "Access token for authentication (will be encoded to base64 UTF-8 and compared with token_encoded) (required)"
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Repository ID to check permissions for (required)"
                        }
                    },
                    "required": ["access_token", "repository_id"]
                }
            }
        }