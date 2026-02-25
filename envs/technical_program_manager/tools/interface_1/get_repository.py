import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class GetRepository(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: Optional[str] = None,
        repository_name: Optional[str] = None,
        program_id: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for repositories"
            })
        
        repositories = data.get("repositories", {})
        
        if not repository_id and not repository_name and not program_id:
            return json.dumps({
                "success": False,
                "error": "At least one parameter (repository_id, repository_name, or program_id) must be provided"
            })
        
        if repository_id:
            if str(repository_id) not in repositories:
                return json.dumps({
                    "success": False,
                    "error": f"Repository with ID '{repository_id}' not found"
                })
            
            repository = repositories[str(repository_id)]
            
            if program_id and str(repository.get("project_id")) != str(program_id):
                return json.dumps({
                    "success": False,
                    "error": f"Repository does not belong to program '{program_id}'"
                })
            
            repository_data = {
                "repository_id": str(repository_id),
                "repository_name": str(repository.get("repository_name", "")),
                "description": str(repository.get("description", "")) if repository.get("description") is not None else None,
                "default_branch": str(repository.get("default_branch", "main")),
                "program_id": str(repository.get("project_id", "")) if repository.get("project_id") is not None else None,
                "created_at": str(repository.get("created_at", "")),
                "updated_at": str(repository.get("updated_at", ""))
            }
            
            return json.dumps({
                "success": True,
                "repository_data": repository_data
            })
        
        if repository_name or program_id:
            found_repositories = []
            
            for rid, repository in repositories.items():
                if repository_name and repository.get("repository_name") != repository_name:
                    continue
                
                if program_id and str(repository.get("project_id")) != str(program_id):
                    continue
                
                repository_data = {
                    "repository_id": str(rid),
                    "repository_name": str(repository.get("repository_name", "")),
                    "description": str(repository.get("description", "")) if repository.get("description") is not None else None,
                    "default_branch": str(repository.get("default_branch", "main")),
                    "program_id": str(repository.get("project_id", "")) if repository.get("project_id") is not None else None,
                    "created_at": str(repository.get("created_at", "")),
                    "updated_at": str(repository.get("updated_at", ""))
                }
                found_repositories.append(repository_data)
            
            if not found_repositories:
                search_term = f"name '{repository_name}'" if repository_name else f"program '{program_id}'"
                return json.dumps({
                    "success": False,
                    "error": f"No repository found with {search_term} matching the specified filters"
                })
            
            if len(found_repositories) == 1:
                return json.dumps({
                    "success": True,
                    "repository_data": found_repositories[0]
                })
            
            return json.dumps({
                "success": True,
                "multiple_results": True,
                "count": int(len(found_repositories)),
                "repositories": found_repositories
            })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_repository",
                "description": "Retrieves code repository information. Use this to verify repository setup for projects, get repository details for engineering progress checks, validate code storage locations, or identify repositories for pull request queries.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository"
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "The name of the repository"
                        },
                        "program_id": {
                            "type": "string",
                            "description": "Filter results by program ID. If provided alone, lists all repositories for that program"
                        }
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["repository_id"]},
                        {"required": ["repository_name"]},
                        {"required": ["program_id"]}
                    ]
                }
            }
        }
