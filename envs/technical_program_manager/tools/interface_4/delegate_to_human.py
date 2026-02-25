from typing import Any, Dict
import json
from tau_bench.envs.tool import Tool


class DelegateToHuman(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        summary: str,
    ) -> str:
        if not summary:
            return json.dumps(
                {
                    "success": False,
                    "error": "Missing required parameter: 'summary'",
                }
            )
        return json.dumps(
            {"success": True, "message": "Delegation successful", "summary": summary}
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "delegate_to_human",
                "description": "Delegate the user to a human agent, with a summary of the user's issue. Only delegate if the user explicitly asks for a human agent, or if the user's issue cannot be resolved by the agent with the available tools.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "A summary of the user's issue.",
                        },
                    },
                    "required": [
                        "summary",
                    ],
                },
            },
        }