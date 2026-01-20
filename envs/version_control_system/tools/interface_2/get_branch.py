import json
from typing import Any, Dict, Optional, Tuple
from tau_bench.envs.tool import Tool


class GetBranch(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        branch_name: str,
        repository_id: str,
    ) -> str:

        def find_branch(branches_dict: Dict[str, Any], repository_id_str: str, branch_name_str: str) -> Optional[Dict[str, Any]]:
            
            for bid, branch in branches_dict.items():
                if not isinstance(branch, dict):
                    continue
                
                if str(branch.get("repository_id")) == repository_id_str and str(branch.get("branch_name", "")).strip() == branch_name_str:
                    branch_info = branch.copy()
                    branch_info["branch_id"] = str(bid)
                    return branch_info
            
            return None

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        # Get data containers
        branches_dict = data.get("branches", {})

        # Convert to strings
        branch_name_str = str(branch_name).strip()
        repository_id_str = str(repository_id).strip()

        # Find branch
        branch = find_branch(branches_dict, repository_id_str, branch_name_str)

        if not branch:
            return json.dumps({
                "success": False,
                "error": f"Branch '{branch_name_str}' not found in repository '{repository_id_str}'"
            })

        return json.dumps({
            "success": True,
            "branch": branch,
            "message": f"Branch '{branch_name_str}' found in repository '{repository_id_str}'",
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        
        return {
            "type": "function",
            "function": {
                "name": "get_branch",
                "description": (
                    "Retrieve branch information using the branch name and repository. Returns full branch details, or an error if required inputs are missing or the branch does not exist."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "branch_name": {
                            "type": "string",
                            "description": "The name of the branch to retrieve.",
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository containing the branch.",
                        },
                    },
                    "required": ["branch_name", "repository_id"],
                },
            },
        }