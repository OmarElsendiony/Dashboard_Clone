import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ListBranches(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: Optional[str] = None,
        branch_name: Optional[str] = None,
        is_default: Optional[bool] = None,
        branch_id: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for branches"
            })
        
        # Validate is_default if provided (must be boolean)
        if is_default is not None and not isinstance(is_default, bool):
            return json.dumps({
                "success": False,
                "error": f"Invalid is_default value. Must be True or False"
            })
        
        branches = data.get("branches", {})
        results = []
        
        for b_id, branch_data in branches.items():
            # Apply filters
            if repository_id and branch_data.get("repository_id") != repository_id:
                continue
            if branch_name and branch_data.get("branch_name") != branch_name:
                continue
            if is_default is not None and branch_data.get("is_default") != is_default:
                continue
            if branch_id and b_id != branch_id:
                continue
            
            results.append({**branch_data, "branch_id": b_id})
        
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
                "name": "list_branches",
                "description": "Lists branches from repositories.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Filter by repository_id (exact match) (optional)"
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "Filter by branch name (exact match) (optional)"
                        },
                        "is_default": {
                            "type": "boolean",
                            "description": "Filter by default branch status. Allowed values: True, False (optional)"
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "Filter by branch_id (exact match) (optional)"
                        }
                    },
                    "required": []
                }
            }
        }

