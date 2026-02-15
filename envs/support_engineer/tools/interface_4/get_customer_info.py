import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetCustomerInfo(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        customer_id: Optional[str] = None,
        customer_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        if not any([customer_id, customer_name, email]):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one parameter must be provided: customer_id, customer_name, or email",
                }
            )

        customers = data.get("customers", {})
        subscriptions = data.get("subscriptions", {})

        results = []
        for customer in customers.values():
            if customer_id is not None and str(customer.get("customer_id")) != str(
                customer_id
            ):
                continue

            if customer_name is not None and customer_name.lower() not in customer.get(
                "customer_name", ""
            ).lower():
                continue

            if email is not None and email.lower() != customer.get(
                "email", ""
            ).lower():
                continue

            customer_subs = [
                {"subscription_id": sub.get("subscription_id"), "status": sub.get("status")}
                for sub in subscriptions.values()
                if str(sub.get("customer_id")) == str(customer.get("customer_id"))
            ]

            customer_response = {
                "customer_id": customer.get("customer_id"),
                "customer_name": customer.get("customer_name"),
                "email": customer.get("email"),
                "status": customer.get("status"),
                "subscriptions": customer_subs,
            }
            results.append(customer_response)

        return json.dumps({"success": True, "customers": results})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_customer_info",
                "description": "Get customer information and subscription details by identifier, name, or email.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "Filter by customer identifier",
                        },
                        "customer_name": {
                            "type": "string",
                            "description": "Filter by customer name substring",
                        },
                        "email": {
                            "type": "string",
                            "description": "Filter by exact email match (case-insensitive). Email is a unique identifier.",
                        },
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["customer_id"]},
                        {"required": ["customer_name"]},
                        {"required": ["email"]},
                    ]
                },
            },
        }
