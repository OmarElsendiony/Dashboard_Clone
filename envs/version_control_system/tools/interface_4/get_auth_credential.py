import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool
import base64


class GetAuthCredential(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], user_email: str) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        access_tokens = data.get("access_tokens", {})
        users = data.get("users", {})
        user_info = next(
            (user for user in users.values() if user.get("email") == user_email), None
        )
        if not user_info:
            return json.dumps({"success": False, "error": "User not found"})
        else:
            user_id = user_info.get("user_id")
        encoded_token = next(
            (
                info.get("token_encoded")
                for info in access_tokens.values()
                if info.get("user_id") == user_id
            ),
            None,
        )

        def decode(encoded_text):
            """
            Decodes Base64 text back to the original word.
            """
            encoded_bytes = encoded_text.encode("utf-8")
            decoded_bytes = base64.b64decode(encoded_bytes)
            return decoded_bytes.decode("utf-8")

        # decode the encoded token
        if encoded_token:
            decoded_token = decode(encoded_token)
            return json.dumps(
                {"success": True, "auth_token": decoded_token, "user": user_info}
            )
        else:
            return json.dumps({"success": False, "error": "User not authenticated"})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_auth_credential",
                "description": "Retrieve authentication credentials for a user of the version control system using the user email address.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_email": {
                            "type": "string",
                            "description": "The email address of the user whose authentication credentials are to be retrieved.",
                        }
                    },
                    "required": ["user_email"],
                },
            },
        }
