import json
from typing import Any, Dict, List
from tau_bench.envs.tool import Tool


class SearchBranch(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        branch_name: str,
    ) -> str:

        def find_branches(branches_dict: Dict[str, Any], repository_id_str: str, branch_name_str: str) -> List[Dict[str, Any]]:
            matching_branches = []
            branch_name_lower = branch_name_str.lower()

            for bid, branch in branches_dict.items():
                if not isinstance(branch, dict):
                    continue

                if str(branch.get("repository_id", "")) == repository_id_str:
                    current_branch_name = str(branch.get("branch_name", "")).strip()
                    if branch_name_lower in current_branch_name.lower():
                        branch_info = branch.copy()
                        branch_info["branch_id"] = str(bid)
                        matching_branches.append(branch_info)

            return matching_branches

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        if not repository_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'repository_id'"})

        if not branch_name:
            return json.dumps({"success": False, "error": "Missing required parameter: 'branch_name'"})

        repositories_dict = data.get("repositories", {})
        branches_dict = data.get("branches", {})
        users_dict = data.get("users", {})

        repository_id_str = str(repository_id).strip()
        branch_name_str = str(branch_name).strip()

        if not branch_name_str:
            return json.dumps({
                "success": False,
                "error": "Branch name cannot be empty"
            })

        if repository_id_str not in repositories_dict:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repository_id_str}' not found"
            })

        repository = repositories_dict[repository_id_str]

        if not isinstance(repository, dict):
            return json.dumps({
                "success": False,
                "error": f"Invalid repository data structure for repository ID '{repository_id_str}'"
            })

        # Find matching branches
        matching_branches = find_branches(branches_dict, repository_id_str, branch_name_str)

        if not matching_branches:
            return json.dumps({
                "success": False,
                "error": f"No branches matching '{branch_name_str}' found in repository '{repository_id_str}'"
            })

        enriched_branches = []
        for branch in matching_branches:
            enriched_branch = branch.copy()

            created_by = str(branch.get("created_by", ""))
            if created_by and str(created_by) in users_dict:
                creator = users_dict[str(created_by)]
                if isinstance(creator, dict):
                    enriched_branch["creator_email"] = str(creator.get("email", ""))
                    enriched_branch["creator_name"] = str(f"{creator.get('first_name', '')} {creator.get('last_name', '')}".strip())

            enriched_branch["repository_name"] = str(repository.get("repository_name", ""))

            enriched_branches.append(enriched_branch)

        enriched_branches.sort(
            key=lambda b: (
                str(b.get("branch_name", "")).strip().lower() != branch_name_str.lower(),
                b.get("created_at", "")
            ),
            reverse=False
        )

        message = f"Found {len(enriched_branches)} branch(es) matching '{branch_name_str}' in repository '{repository_id_str}'"

        return json.dumps({
            "success": True,
            "branches": enriched_branches,
            "count": int(len(enriched_branches)),
            "message": message,
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the search_branch function."""
        return {
            "type": "function",
            "function": {
                "name": "search_branch",
                "description": (
                    "Searches for branches within a repository by name. "
                    "This function locates branches matching the specified name pattern, supporting both exact and partial matches. "
                    "Use this when verifying branch existence before creation, locating branches for specific tickets or fixes, "
                    "or finding branches related to particular features or issues."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository to search within.",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "The name or partial name of the branch to search for.",
                        },
                    },
                    "required": ["repository_id", "branch_name"],
                },
            },
        }
