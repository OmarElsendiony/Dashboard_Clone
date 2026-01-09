import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class EstablishOrganization(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        organization_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[str] = "public",
        plan_type: Optional[str] = "free"
    ) -> str:
        """
        Creates a new organization in the version control system.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not organization_name:
            return json.dumps({"success": False, "error": "organization_name is required to establish an organization"})

        organizations = data.get("organizations", {})

        # Check if organization name already exists
        for org_id, org in organizations.items():
            if org.get("organization_name") == organization_name:
                return json.dumps({"success": False, "error": f"Organization with name '{organization_name}' already exists"})

        # Validate visibility
        valid_visibilities = ["public", "limited", "private"]
        if visibility not in valid_visibilities:
            return json.dumps({"success": False, "error": f"Invalid visibility '{visibility}'. Valid values: public, limited, private"})

        # Validate plan_type
        valid_plan_types = ["free"]
        if plan_type not in valid_plan_types:
            return json.dumps({"success": False, "error": f"Invalid plan_type '{plan_type}'. Valid values: free"})

        # Generate new organization_id
        if organizations:
            max_id = max(int(k) for k in organizations.keys())
            new_id = str(max_id + 1)
        else:
            new_id = "1"

        # Create organization record
        new_org = {
            "organization_id": new_id,
            "organization_name": organization_name,
            "visibility": visibility,
            "display_name": display_name,
            "description": description,
            "plan_type": plan_type,
            "created_at": "2026-01-01T23:59:00",
            "updated_at": "2026-01-01T23:59:00"
        }

        organizations[new_id] = new_org

        return json.dumps({"success": True, "result": new_org})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "establish_organization",
                "description": "Creates a new organization in the version control system. The organization name must be unique.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "organization_name": {
                            "type": "string",
                            "description": "The unique name for the new organization. Must not already exist in the system."
                        },
                        "display_name": {
                            "type": "string",
                            "description": "A display name for the organization. Optional."
                        },
                        "description": {
                            "type": "string",
                            "description": "A text description of the organization. Optional."
                        },
                        "visibility": {
                            "type": "string",
                            "description": "The visibility level of the organization. Valid values: public, limited, private. Default: public."
                        },
                        "plan_type": {
                            "type": "string",
                            "description": "The subscription plan type for the organization. Valid values: free"
                        }
                    },
                    "required": ["organization_name"]
                }
            }
        }