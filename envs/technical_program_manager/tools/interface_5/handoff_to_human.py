import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class HandoffToHuman(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        summary: Optional[str] = None,
    ) -> str:
        if not summary:
            return json.dumps(
                {"success": True, "Message": "Handoff to human agent successful."}
            )
        return json.dumps(
            {
                "success": True,
                "Message": f"Handoff to human agent successful. Summary: {summary}",
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "handoff_to_human",
                "description": "Transfer the user to a human agent, if the user's issue cannot be resolved by the agent with the available tools.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "A summary of the user's issue.",
                        },
                    },
                    "required": [],
                },
            },
        }
