import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ListStars(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        repository_id: Optional[str] = None
    ) -> str:
        stars = data.get("stars", {})
        users = data.get("users", {})
        repositories = data.get("repositories", {})

        # Validate existence of provided IDs
        if user_id and user_id not in users:
            return json.dumps({"error": f"User {user_id} not found"})
        
        if repository_id and repository_id not in repositories:
            return json.dumps({"error": f"Repository {repository_id} not found"})

        results = []
        for star in stars.values():
            match = True
            if user_id and star.get("user_id") != user_id:
                match = False
            if repository_id and star.get("repository_id") != repository_id:
                match = False

            if match:
                results.append(star)

        return json.dumps(results)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_stars",
                "description": "Lists repository stars filtered by user or repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "Filter stars by user ID (optional)"
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Filter stars by repository ID (optional)"
                        }
                    },
                    "required": []
                }
            }
        }