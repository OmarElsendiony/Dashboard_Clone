import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class VerifyUserAuthentication(Tool):

    @staticmethod
    def invoke(data: Dict[str, Any], user_id: str) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not user_id:
            return json.dumps({"success": False, "error": "user_id is required to verify user authentication"})

        access_tokens = data.get("access_tokens", {})

        # Search for active, non-expired token for this user
        valid_token = None
        for token_id, token in access_tokens.items():
            if str(token.get("user_id")) == str(user_id):
                token_status = token.get("status")
                if token_status == "active":
                    valid_token = token
                    break

        if not valid_token:
            return json.dumps({"success": False, "error": f"No active access token found for user_id '{user_id}'. User must have a valid authentication token to perform operations."})

        return json.dumps({"success": True, "result": valid_token})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "verify_user_authentication",
                "description": "Validates that a user has an active access token in the version control system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The unique identifier of the user whose authentication needs to be verified."
                        }
                    },
                    "required": ["user_id"]
                }
            }
        }
