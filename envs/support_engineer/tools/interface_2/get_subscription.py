import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetSubscription(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        customer_id: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        if not customer_id:
            return json.dumps({"success": False, "error": "Missing required parameter: 'customer_id'"})

        subscriptions_dict = data.get("subscriptions", {})
        search_id = str(customer_id).strip()

        found_subs = []
        for _, s_data in subscriptions_dict.items():
            if str(s_data.get("customer_id", "")) == search_id:
                found_subs.append(s_data)

        if not found_subs:
            return json.dumps(
                {
                    "success": False,
                    "error": f"No subscription found for customer ID '{search_id}'",
                }
            )

        target_subscription = found_subs[0]
        for sub in found_subs:
            if sub.get("status") == "active":
                target_subscription = sub
                break

        response = {
            "subscription_id": str(target_subscription.get("subscription_id", "")),
            "customer_id": str(target_subscription.get("customer_id", "")),
            "tier": str(target_subscription.get("tier", "Basic")),
            "status": str(target_subscription.get("status", "active")),
            "start_date": str(target_subscription.get("start_date", "")),
            "end_date": (
                str(target_subscription.get("end_date", ""))
                if target_subscription.get("end_date")
                else None
            ),
            "created_at": str(target_subscription.get("created_at", None)),
            "updated_at": str(target_subscription.get("updated_at", None)),
        }

        return json.dumps({"success": True, "subscription": response})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_subscription",
                "description": (
                    "Retrieves customer subscription tier and status information. "
                    "This function validates customer support entitlements and service level agreements. "
                    "Use this after ticket intake to check SLA compliance, "
                    "when Basic tier customers require scope verification, "
                    "for SLA breach detection against resolution time targets, "
                    "or to confirm expired subscription status before processing."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The unique identifier of the customer whose subscription details are required.",
                        }
                    },
                    "required": ["customer_id"],
                },
            },
        }
