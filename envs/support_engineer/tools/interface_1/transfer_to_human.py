import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool

class TransferToHuman(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        summary: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": bool(False), "error": str("Invalid data format")})

        if not summary:
             return json.dumps({"success": bool(False), "error": str("Missing Argument: 'summary' is required.")})

        if not isinstance(summary, str) or not summary.strip():
            return json.dumps({"success": bool(False), "error": str("Invalid Argument: summary must be a non-empty string.")})

        return json.dumps({
            "success": bool(True),
            "message": str("Transfer successful"),
            "summary": str(summary)
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "transfer_to_human",
                "description": "Transfers the user to a human agent, with a summary of the user's issue. Only transfer if the user explicitly asks for a human agent, or if the user's issue cannot be resolved by the agent with the available tools.",
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
