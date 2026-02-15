import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class GetUser(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        email: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format: 'data' must be a dict"})

        if not email:
            return json.dumps({"success": False, "error": "Missing required parameter: 'email'"})

        users_dict = data.get("users", {})
        email_clean = str(email).strip().lower()

        # Find user by email (avoiding direct ID requirement as per rule 8 of common errors)
        user_match = None
        user_id_found = None
        for uid, user_data in users_dict.items():
            if str(user_data.get("email", "")).lower() == email_clean:
                user_match = user_data
                user_id_found = uid
                break

        if not user_match:
            return json.dumps({
                "success": False,
                "error": f"User with email '{email_clean}' not found"
            })

        # Prepare response following schema datatypes
        # Casting role and status to ensure deterministic string returns for enums
        response_user = {
            "user_id": str(user_id_found),
            "username": str(user_match.get("username", "")),
            "email": str(user_match.get("email", "")),
            "first_name": str(user_match.get("first_name", "")),
            "last_name": str(user_match.get("last_name", "")),
            "role": str(user_match.get("role", "support_engineer")),
            "status": str(user_match.get("status", "active")),
            "created_at": str(user_match.get("created_at", "")),
            "updated_at": str(user_match.get("updated_at", ""))
        }

        # Include technical_expertise only if it exists in the schema for that user
        if "technical_expertise" in user_match:
            response_user["technical_expertise"] = str(user_match["technical_expertise"])

        return json.dumps({
            "success": True,
            "user": response_user
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_user",
                "description": "Retrieves user profile information including role, status, and technical expertise. "
                    "This function authenticates support engineers and verifies their permissions and availability. "
                    "Use this at the start of ticket processing to validate user authentication, "
                    "before requesting PR reviews to ensure reviewer eligibility, "
                    "or when assigning tasks to confirm user active status and expertise.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "The unique email address of the user to retrieve details for."
                        }
                    },
                    "required": ["email"]
                }
            }
        }
