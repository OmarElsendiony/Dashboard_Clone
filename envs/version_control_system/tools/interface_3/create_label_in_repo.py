import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateLabelInRepo(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        label_name: str,
        color: str,
        description: Optional[str] = None
    ) -> str:
        """
        Creates a new label in a repository.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required to create a label"})
        if not label_name:
            return json.dumps({"success": False, "error": "label_name is required to create a label"})
        if not color:
            return json.dumps({"success": False, "error": "color is required to create a label"})

        repositories = data.get("repositories", {})
        labels = data.get("labels", {})

        # Validate repository exists
        if str(repository_id) not in repositories:
            return json.dumps({"success": False, "error": f"Repository with id '{repository_id}' not found"})

        # Check if label with same name already exists in the repository
        for label in labels.values():
            if str(label.get("repository_id")) == str(repository_id) and label.get("label_name") == label_name:
                return json.dumps({"success": False, "error": f"Label with name '{label_name}' already exists in this repository"})

        # Generate new label_id
        if labels:
            max_id = max(int(k) for k in labels.keys())
            new_label_id = str(max_id + 1)
        else:
            new_label_id = "1"

        # Create label record
        new_label = {
            "label_id": new_label_id,
            "repository_id": repository_id,
            "label_name": label_name,
            "color": color,
            "pr_ids": None,
            "issue_ids": None,
            "description": description,
            "created_at": "2026-01-01T23:59:00"
        }

        labels[new_label_id] = new_label

        return json.dumps({"success": True, "result": new_label})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_label_in_repo",
                "description": "Creates a new label in a repository. Labels can be used to categorize issues and pull requests.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository where the label will be created."
                        },
                        "label_name": {
                            "type": "string",
                            "description": "The name of the label (e.g., bug, enhancement, documentation)."
                        },
                        "color": {
                            "type": "string",
                            "description": "The color of the label in hex format (e.g., #FF0000 for red)."
                        },
                        "description": {
                            "type": "string",
                            "description": "A brief description of the label's purpose. Optional."
                        }
                    },
                    "required": ["repository_id", "label_name", "color"]
                }
            }
        }