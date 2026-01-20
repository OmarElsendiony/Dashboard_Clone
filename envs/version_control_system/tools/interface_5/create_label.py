import json
import random
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreateLabel(Tool):
   
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repo_id: str,
        label_name: str,
    ) -> str:
      

        def generate_id(table: Dict[str, Any]) -> str:
         
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        def generate_random_color() -> str:
           
            return "#{:06x}".format(random.randint(0, 0xFFFFFF))

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

        repository = repositories[repo_id]

        # Check if repository is archived
        if repository.get("is_archived", False):
            return json.dumps({
                "success": False,
                "error": f"Cannot create label in archived repository '{repo_id}'"
            })

        # Check if label with same name already exists in this repository (case-insensitive)
        for _, label in labels.items():
            if (
                str(label.get("repository_id")) == repo_id
                and label.get("label_name", "").strip().lower() == label_name.lower()
            ):
                return json.dumps({
                    "success": False,
                    "error": f"Label '{label_name}' already exists in repository '{repo_id}'"
                })

        # Generate random color for the label
        color = generate_random_color()

        # Generate new label ID
        new_label_id = generate_id(labels)

        # Set timestamp for created_at
        timestamp = "2026-01-01T23:59:00"

        # Create new label record
        new_label = {
            "label_id": new_label_id,
            "repository_id": repo_id,
            "label_name": label_name,
            "color": color,
            "description": "",
            "issue_ids": None,
            "pr_ids": None,
            "created_at": timestamp,
        }

        # Add the new label to the labels dictionary
        labels[new_label_id] = new_label

        # Build response with parsed data (matching get_label response format)
        label_data = {
            "label_id": new_label.get("label_id"),
            "repository_id": new_label.get("repository_id"),
            "label_name": new_label.get("label_name"),
            "color": new_label.get("color"),
            "description": new_label.get("description"),
            "issue_ids": [],
            "pr_ids": [],
            "created_at": new_label.get("created_at"),
        }

        return json.dumps({
            "success": True,
            "message": f"Label '{label_name}' created successfully in repository '{repo_id}'",
            "label_data": label_data
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_label",
                "description": "Creates a new label in a repository in the version control system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo_id": {
                            "type": "string",
                            "description": "The ID of the repository to create the label in.",
                        },
                        "label_name": {
                            "type": "string",
                            "description": "The name of the label to create.",
                        },
                    },
                    "required": ["repo_id", "label_name"],
                },
            },
        }
