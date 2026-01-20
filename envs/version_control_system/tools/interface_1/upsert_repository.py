import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpsertRepository(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        access_token: str,
        repository_name: str,
        owner_type: str,
        owner_id: str,
        description: Optional[str] = None,
        visibility: Optional[str] = None,
        default_branch: Optional[str] = None,
        is_template: Optional[bool] = None,
        license_type: Optional[str] = None,
        is_archived: Optional[bool] = None,
        repository_id: Optional[str] = None,
        forks_count: Optional[int] = None,
        stars_count: Optional[int] = None
    ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        def get_user_from_token(token: str, tokens_data: Dict[str, Any]) -> Optional[str]:
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
        
        if action not in ["create", "update"]:
            return json.dumps({
                "success": False,
                "error": f"Invalid action '{action}'. Must be 'create' or 'update'"
            })
        
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })
        
        repositories = data.get("repositories", {})
        users = data.get("users", {})
        organizations = data.get("organizations", {})
        access_tokens = data.get("access_tokens", {})
        
        # Validate access token
        requesting_user_id = get_user_from_token(access_token, access_tokens)
        if not requesting_user_id:
            return json.dumps({
                "success": False,
                "error": "Invalid or expired access token"
            })
        
        timestamp = "2026-01-01T23:59:00"
        
        if action == "create":
            # Validate owner exists
            if owner_type == "user":
                if owner_id not in users:
                    return json.dumps({
                        "success": False,
                        "error": f"User with ID '{owner_id}' not found"
                    })
            elif owner_type == "organization":
                if owner_id not in organizations:
                    return json.dumps({
                        "success": False,
                        "error": f"Organization with ID '{owner_id}' not found"
                    })
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid owner_type '{owner_type}'. Must be 'user' or 'organization'"
                })
            
            # Validate visibility
            if visibility and visibility not in ["public", "private", "internal"]:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid visibility '{visibility}'. Must be 'public', 'private', or 'internal'"
                })
            
            # Validate license_type
            if license_type and license_type not in ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "unlicensed", "other"]:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid license_type '{license_type}'. Must be one of: 'MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause', 'unlicensed', 'other'"
                })
            
            # Check for duplicate repository name for owner
            for repo in repositories.values():
                if (repo.get("repository_name") == repository_name and 
                    repo.get("owner_id") == owner_id and
                    repo.get("owner_type") == owner_type):
                    return json.dumps({
                        "success": False,
                        "error": f"Repository '{repository_name}' already exists for this owner"
                    })
            
            new_repo_id = generate_id(repositories)
            
            new_repo = {
                "repository_id": new_repo_id,
                "repository_name": repository_name,
                "owner_type": owner_type,
                "owner_id": owner_id,
                "description": description,
                "visibility": visibility if visibility else "private",
                "default_branch": default_branch if default_branch else "main",
                "is_fork": False,
                "parent_repository_id": None,
                "is_archived": bool(is_archived) if is_archived is not None else False,
                "is_template": bool(is_template) if is_template is not None else False,
                "stars_count": stars_count if stars_count is not None else 0,
                "forks_count": forks_count if forks_count is not None else 0,
                "license_type": license_type,
                "created_at": timestamp,
                "updated_at": timestamp,
                "pushed_at": None
            }
            
            repositories[new_repo_id] = new_repo
            
            return json.dumps({
                "success": True,
                "action": "create",
                "repository_id": new_repo_id,
                "repository_data": new_repo
            })
        
        elif action == "update":
            # repository_id is required for update
            if not repository_id:
                return json.dumps({
                    "success": False,
                    "error": "repository_id is required for update action"
                })
            
            if repository_id not in repositories:
                return json.dumps({
                    "success": False,
                    "error": f"Repository with ID '{repository_id}' not found"
                })
            
            repo = repositories[repository_id]
            
            # Validate owner exists if being updated
            if owner_type == "user":
                if owner_id not in users:
                    return json.dumps({
                        "success": False,
                        "error": f"User with ID '{owner_id}' not found"
                    })
            elif owner_type == "organization":
                if owner_id not in organizations:
                    return json.dumps({
                        "success": False,
                        "error": f"Organization with ID '{owner_id}' not found"
                    })
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid owner_type '{owner_type}'. Must be 'user' or 'organization'"
                })
            
            # Validate visibility if provided
            if visibility and visibility not in ["public", "private", "internal"]:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid visibility '{visibility}'. Must be 'public', 'private', or 'internal'"
                })
            
            # Validate license_type if provided
            if license_type and license_type not in ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "unlicensed", "other"]:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid license_type '{license_type}'. Must be one of: 'MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause', 'unlicensed', 'other'"
                })
            
            # Check for duplicate repository name if name/owner is being changed
            if (repository_name != repo.get("repository_name") or 
                owner_id != repo.get("owner_id") or 
                owner_type != repo.get("owner_type")):
                for other_repo_id, other_repo in repositories.items():
                    if other_repo_id != repository_id:
                        if (other_repo.get("repository_name") == repository_name and 
                            other_repo.get("owner_id") == owner_id and
                            other_repo.get("owner_type") == owner_type):
                            return json.dumps({
                                "success": False,
                                "error": f"Repository '{repository_name}' already exists for this owner"
                            })
            
            # Update fields
            repo["repository_name"] = repository_name
            repo["owner_type"] = owner_type
            repo["owner_id"] = owner_id
            if description is not None:
                repo["description"] = description
            if visibility is not None:
                repo["visibility"] = visibility
            if default_branch is not None:
                repo["default_branch"] = default_branch
            if is_template is not None:
                repo["is_template"] = is_template
            if license_type is not None:
                repo["license_type"] = license_type
            if is_archived is not None:
                repo["is_archived"] = is_archived
            if forks_count is not None:
                repo["forks_count"] = forks_count
            if stars_count is not None:
                repo["stars_count"] = stars_count
            
            repo["updated_at"] = timestamp
            
            return json.dumps({
                "success": True,
                "action": "update",
                "repository_id": repository_id,
                "repository_data": repo
            })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "upsert_repository",
                "description": "Creates or updates a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Action to perform. Allowed values: 'create', 'update' (required)",
                            "enum": ["create", "update"]
                        },
                        "access_token": {
                            "type": "string",
                            "description": "Access token for authentication (required)"
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "Name of the repository (required)"
                        },
                        "owner_type": {
                            "type": "string",
                            "description": "Type of owner. Allowed values: 'user', 'organization' (required)",
                            "enum": ["user", "organization"]
                        },
                        "owner_id": {
                            "type": "string",
                            "description": "ID of the owner (user_id or organization_id) (required)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Repository description (optional)"
                        },
                        "visibility": {
                            "type": "string",
                            "description": "Repository visibility. Allowed values: 'public', 'private', 'internal' (optional, defaults to 'private' for create)",
                            "enum": ["public", "private", "internal"]
                        },
                        "default_branch": {
                            "type": "string",
                            "description": "Default branch name (optional, defaults to 'main' for create)"
                        },
                        "is_template": {
                            "type": "boolean",
                            "description": "Whether repository is a template. Allowed values: True, False (optional, defaults to False for create)"
                        },
                        "license_type": {
                            "type": "string",
                            "description": "Repository license type. Allowed values: 'MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause', 'unlicensed', 'other' (optional)",
                            "enum": ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "unlicensed", "other"]
                        },
                        "is_archived": {
                            "type": "boolean",
                            "description": "Whether repository is archived. Allowed values: True, False (optional, defaults to False for create)"
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Repository ID (required for update action)"
                        },
                        "forks_count": {
                            "type": "integer",
                            "description": "Number of forks (optional)"
                        },
                        "stars_count": {
                            "type": "integer",
                            "description": "Number of stars (optional)"
                        }
                    },
                    "required": ["action", "access_token", "repository_name", "owner_type", "owner_id"]
                }
            }
        }
