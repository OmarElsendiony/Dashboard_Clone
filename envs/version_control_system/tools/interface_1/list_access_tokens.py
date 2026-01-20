import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ListAccessTokens(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        user_id: str
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format for access tokens"
            })
        
        access_tokens = data.get("access_tokens", {})
        results = []
        
        for token_id, token_data in access_tokens.items():
            if user_id and token_data.get("user_id") != user_id:
                continue

            # Decode first
            token_decoded = None
            try:
                token_encoded = token_data.get("token_encoded", "")
                token_decoded = base64.b64decode(token_encoded).decode("utf-8")
            except Exception:
                token_decoded = None

            # Copy token_data so original is untouched
            safe_token_data = token_data.copy()
            safe_token_data.pop("token_encoded", None)

            result_entry = {
                **safe_token_data,
                "token_id": token_id,
                "token": token_decoded
            }
            results.append(result_entry)

        
        return json.dumps({
            "success": True,
            "count": len(results),
            "results": results
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_access_tokens",
                "description": "Lists access tokens for a user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "Filter by user_id (exact match)"
                        }
                    },
                    "required": ["user_id"]
                }
            }
        }