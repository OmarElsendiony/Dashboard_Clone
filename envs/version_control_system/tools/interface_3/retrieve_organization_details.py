import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class RetrieveOrganizationDetails(Tool):

    @staticmethod
    def invoke(data: Dict[str, Any], organization_name: str) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not organization_name:
            return json.dumps({"success": False, "error": "organization_name is required to retrieve organization details"})

        organizations = data.get("organizations", {})

        # Search for organization by name
        found_org = None
        for org_id, org in organizations.items():
            if org.get("organization_name") == organization_name:
                found_org = org
                break

        if not found_org:
            return json.dumps({"success": False, "error": f"Organization with name '{organization_name}' not found in the system"})

        return json.dumps({"success": True, "result": found_org})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "retrieve_organization_details",
                "description": "Retrieves an organization's information by its name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "organization_name": {
                            "type": "string",
                            "description": "The name of the organization to look up."
                        }
                    },
                    "required": ["organization_name"]
                }
            }
        }
