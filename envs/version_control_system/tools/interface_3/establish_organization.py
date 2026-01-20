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
        visibility: Optional[str] = "public"
    ) -> str:
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
            "plan_type": "free",
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
                "description": "Creates a new organization in the version control system.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "organization_name": {
                            "type": "string",
                            "description": "The unique name for the new organization."
                        },
                        "display_name": {
                            "type": "string",
                            "description": "A display name for the organization (optional)."
                        },
                        "description": {
                            "type": "string",
                            "description": "A text description of the organization (optional)."
                        },
                        "visibility": {
                            "type": "string",
                            "description": "The visibility level of the organization. Valid values: public, limited, private. Default: public."
                        }
                    },
                    "required": ["organization_name"]
                }
            }
        }