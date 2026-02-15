import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetCustomer(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        customer_name: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        if not customer_name:
            return json.dumps({"success": False, "error": "Missing required parameter: 'customer_name'"})

        customers_dict = data.get("customers", {})
        search_name = str(customer_name).strip().lower()

        target_customer = None
        target_customer_id = None

        for c_id, c_data in customers_dict.items():
            if str(c_data.get("customer_name", "")).strip().lower() == search_name:
                target_customer = c_data
                target_customer_id = c_id
                break

        if not target_customer:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Customer with name '{customer_name}' not found",
                }
            )

        response = {
            "customer_id": str(target_customer_id),
            "customer_name": str(target_customer.get("customer_name", "")),
            "email": str(target_customer.get("email", "")),
            "status": str(target_customer.get("status", "active")),
            "sla_contract_type": str(
                target_customer.get("sla_contract_type", "Standard")
            ),
            "created_at": str(target_customer.get("created_at", None)),
            "updated_at": str(target_customer.get("updated_at", None)),
        }

        return json.dumps({"success": True, "customer": response})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_customer",
                "description": (
                    "Retrieves customer account status and SLA contract details. "
                    "This function validates customer entitlement and support eligibility. "
                    "Use this during ticket intake to extract customer_id for subscription lookup, "
                    "before processing Basic tier scope verification, "
                    "or as first step in customer entitlement validation workflow."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_name": {
                            "type": "string",
                            "description": "The registered name of the customer entity to retrieve.",
                        }
                    },
                    "required": ["customer_name"],
                },
            },
        }
