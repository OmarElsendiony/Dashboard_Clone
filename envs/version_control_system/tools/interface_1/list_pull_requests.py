import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ListPullRequests(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: Optional[str] = None,
        status: Optional[str] = None,
        author_id: Optional[str] = None,
        source_branch: Optional[str] = None,
        target_branch: Optional[str] = None,
        pull_request_id: Optional[str] = None
    ) -> str:
        """
        List pull requests with optional filters.
        """
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })
        
        # Validate status if provided
        if status and status not in ["open", "closed", "merged", "draft"]:
            return json.dumps({
                "success": False,
                "error": f"Invalid status '{status}'. Must be 'open', 'closed', 'merged', or 'draft'"
            })
        
        pull_requests = data.get("pull_requests", {})
        results = []
        
        for pr_id, pr_data in pull_requests.items():
            # Apply filters
            if repository_id and pr_data.get("repository_id") != repository_id:
                continue
            if status and pr_data.get("status") != status:
                continue
            if author_id and pr_data.get("author_id") != author_id:
                continue
            if source_branch and pr_data.get("source_branch") != source_branch:
                continue
            if target_branch and pr_data.get("target_branch") != target_branch:
                continue
            if pull_request_id and pr_id != pull_request_id:
                continue
            
            results.append({**pr_data, "pull_request_id": pr_id})
        
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
                "name": "list_pull_requests",
                "description": "List pull requests from repositories. Can filter by repository_id, status, author_id, source_branch, target_branch, or pull_request_id. Returns all pull requests if no filters are provided.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Filter by repository_id (exact match)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status. Allowed values: 'open', 'closed', 'merged', 'draft' (exact match)"
                        },
                        "author_id": {
                            "type": "string",
                            "description": "Filter by author_id (exact match)"
                        },
                        "source_branch": {
                            "type": "string",
                            "description": "Filter by source branch name (exact match)"
                        },
                        "target_branch": {
                            "type": "string",
                            "description": "Filter by target branch name (exact match)"
                        },
                        "pull_request_id": {
                            "type": "string",
                            "description": "Filter by pull_request_id (exact match)"
                        }
                    },
                    "required": []
                }
            }
        }

