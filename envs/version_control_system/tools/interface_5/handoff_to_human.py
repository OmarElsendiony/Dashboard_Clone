import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class HandoffToHuman(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        summary: str,
    ) -> str:
        # This tool is a simple escalation hook.
        return json.dumps("Transfer successful")

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "handoff_to_human",
                "description": (
                   "Transfers the user to a human agent with a summary of the user's issue."
                ),
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


