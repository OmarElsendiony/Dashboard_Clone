import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class StarUnstarRepo(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        user_id: str,
        repository_id: str,
        action: str
    ) -> str:
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        timestamp = "2026-01-01T23:59:00"

        try:
            encoded_input_token = base64.b64encode(access_token.encode('utf-8')).decode('utf-8')
        except Exception:
            return json.dumps({"error": "Failed to process access token"})

        tokens = data.get("access_tokens", {})
        valid_token = False
        
        for token in tokens.values():
            if token.get("token_encoded") == encoded_input_token and token.get("status") == "active":
                if token.get("expires_at") > timestamp:
                    valid_token = True
                    break
        
        if not valid_token:
            return json.dumps({"error": "Invalid or expired access token"})

        users = data.get("users", {})
        repositories = data.get("repositories", {})
        stars = data.get("stars", {})

        if user_id not in users:
            return json.dumps({"error": f"User {user_id} not found"})
        if repository_id not in repositories:
            return json.dumps({"error": f"Repository {repository_id} not found"})

        if action not in ['star', 'unstar']:
            return json.dumps({"error": "Invalid action. Must be 'star' or 'unstar'"})

        # Check if already starred
        existing_star_id = None
        for star_id, star in stars.items():
            if star.get("user_id") == user_id and star.get("repository_id") == repository_id:
                existing_star_id = star_id
                break

        if action == 'star':
            if existing_star_id:
                # Idempotent: return existing record
                return json.dumps(stars[existing_star_id])
            else:
                new_id = generate_id(stars)
                new_star = {
                    "star_id": new_id,
                    "user_id": user_id,
                    "repository_id": repository_id,
                    "starred_at": timestamp
                }
                stars[new_id] = new_star
                return json.dumps(new_star)
        
        elif action == 'unstar':
            if existing_star_id:
                record = stars.pop(existing_star_id)
                return json.dumps(record)
            else:
                return json.dumps({"error": "Repository is not starred by this user"})

        return json.dumps({"error": "Unexpected error"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "star_unstar_repo",
                "description": "Stars or unstars a repository for a user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "The access token for authentication."
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user performing the action."
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository to star/unstar."
                        },
                        "action": {
                            "type": "string",
                            "description": "The action to perform. Allowed values: 'star', 'unstar'.",
                            "enum": ["star", "unstar"]
                        }
                    },
                    "required": ["access_token", "user_id", "repository_id", "action"]
                }
            }
        }