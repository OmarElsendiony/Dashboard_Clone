import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetLabel(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        label_name: str,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        labels = data.get("labels", {})
        repositories = data.get("repositories", {})

        # Validate required fields
        if not repo_id:
            return json.dumps({"success": False, "error": "Missing required parameter: repo_id"})

        if not label_name:
            return json.dumps({"success": False, "error": "Missing required parameter: label_name"})

        if not isinstance(label_name, str) or not label_name.strip():
            return json.dumps({"success": False, "error": "label_name must be a non-empty string"})

        # Convert repo_id to string for consistent comparison
        repo_id = str(repo_id)
        label_name = label_name.strip()

        # Validate repository exists
        if repo_id not in repositories:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repo_id}' not found"
            })

        # Search for label by repository_id and label_name (case-insensitive)
        found_label = None
        for _, label in labels.items():
            if (
                str(label.get("repository_id")) == repo_id
                and label.get("label_name", "").strip().lower() == label_name.lower()
            ):
                found_label = label.copy()
                break

        if not found_label:
            return json.dumps({
                "success": False,
                "error": f"Label '{label_name}' not found in repository '{repo_id}'"
            })

        # Parse issue_ids and pr_ids from JSON strings to lists
        issue_ids_str = found_label.get("issue_ids")
        pr_ids_str = found_label.get("pr_ids")

        issue_ids_list = []
        if issue_ids_str:
            try:
                issue_ids_list = json.loads(issue_ids_str)
            except json.JSONDecodeError:
                issue_ids_list = []

        pr_ids_list = []
        if pr_ids_str:
            try:
                pr_ids_list = json.loads(pr_ids_str)
            except json.JSONDecodeError:
                pr_ids_list = []

        # Build the response with parsed data
        label_data = {
            "label_id": found_label.get("label_id"),
            "repository_id": found_label.get("repository_id"),
            "label_name": found_label.get("label_name"),
            "color": found_label.get("color"),
            "description": found_label.get("description"),
            "issue_ids": issue_ids_list,
            "pr_ids": pr_ids_list,
            "created_at": found_label.get("created_at"),
        }

        return json.dumps({
            "success": True,
            "label_data": label_data
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_label",
                "description": "Retrieves information about a label from a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository containing the label.",
                        },
                        "label_name": {
                            "type": "string",
                            "description": "The name of the label to look up (case-insensitive).",
                        },
                    },
                    "required": ["repo_id", "label_name"],
                },
            },
        }
