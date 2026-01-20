import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class ListWorkflows(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str
    ) -> str:
        workflows = data.get("workflows", {})
        repositories = data.get("repositories", {})

        if repository_id not in repositories:
            return json.dumps({"error": f"Repository {repository_id} not found"})

        results = []
        for workflow in workflows.values():
            if workflow.get("repository_id") == repository_id:
                results.append(workflow)

        return json.dumps(results)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_workflows",
                "description": "Lists all CI/CD workflows for a given repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository to list workflows for."
                        }
                    },
                    "required": ["repository_id"]
                }
            }
        }