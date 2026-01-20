import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ListRepositories(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        owner_id: Optional[str] = None,
        owner_type: Optional[str] = None,
        visibility: Optional[str] = None,
        is_archived: Optional[bool] = None,
        repository_name: Optional[str] = None,
        repository_id: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for repositories"
            })
        
        # Validate owner_type if provided
        if owner_type and owner_type not in ["user", "organization"]:
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
        
        # Validate is_archived if provided (must be boolean)
        if is_archived is not None and not isinstance(is_archived, bool):
            return json.dumps({
                "success": False,
                "error": f"Invalid is_archived value. Must be True or False"
            })
        
        repositories = data.get("repositories", {})
        results = []
        
        for repo_id, repo_data in repositories.items():
            # Apply filters
            if owner_id and repo_data.get("owner_id") != owner_id:
                continue
            if owner_type and repo_data.get("owner_type") != owner_type:
                continue
            if visibility and repo_data.get("visibility") != visibility:
                continue
            if is_archived is not None and repo_data.get("is_archived") != is_archived:
                continue
            if repository_name and repo_data.get("repository_name") != repository_name:
                continue
            if repository_id and repo_id != repository_id:
                continue
            
            # Create a filtered copy excluding 'project_id'
            filtered_data = {k: v for k, v in repo_data.items() if k != "project_id"}
            
            # Append the filtered data combined with the repository_id
            results.append({**filtered_data, "repository_id": repo_id})
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "results": results
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_repositories",
                "description": "Lists repositories with optional filters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "owner_id": {
                            "type": "string",
                            "description": "Filter by owner_id (exact match) (optional)"
                        },
                        "owner_type": {
                            "type": "string",
                            "description": "Filter by owner type. Allowed values: 'user', 'organization' (optional)",
                            "enum" : ["user", "organization"]
                        },
                        "visibility": {
                            "type": "string",
                            "description": "Filter by visibility. Allowed values: 'public', 'private', 'internal' (optional)",
                            "enum" : ["public", "private", "internal"]
                        },
                        "is_archived": {
                            "type": "boolean",
                            "description": "Filter by archived status. Allowed values: True, False (optional)"
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "Filter by repository name (exact match) (optional)"
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Filter by repository_id (exact match) (optional)"
                        }
                    },
                    "required": []
                }
            }
        }