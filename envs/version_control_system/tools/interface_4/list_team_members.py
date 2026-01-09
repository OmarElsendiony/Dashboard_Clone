import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool
import base64


class ListTeamMembers(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        auth_token: str,
        entity_type: str,
        entity_id: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})
        access_tokens = data.get("access_tokens", {})

        def encode(text):
            text_bytes = text.encode("utf-8")
            encoded_bytes = base64.b64encode(text_bytes)
            return encoded_bytes.decode("utf-8")

        encoded_token = encode(auth_token)

        token_info = next(
            (
                info
                for info in access_tokens.values()
                if info.get("token_encoded") == encoded_token
            ),
            None,
        )

        if not token_info:
            return json.dumps(
                {"success": False, "error": "Invalid authentication token"}
            )
        if entity_type not in {"organization", "project", "repository"}:
            return json.dumps({"success": False, "message": "Invalid entity type"})

        tables = {
            "organization": "organization_members",
            "project": "project_members",
            "repository": "repository_collaborators",
        }
        table_ids = {
            "organization": "organization_id",
            "project": "project_id",
            "repository": "repository_id",
        }
        entities = data.get(tables[entity_type], {})

        target_entities = [
            m for m in entities.values() if m[f"{table_ids[entity_type]}"] == entity_id
        ]
        return json.dumps({"success": True, f"{tables[entity_type]}": target_entities})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_team_members",
                "description": (
                    "Retrieves the list of members associated with a specific entity. "
                    "The entity can be an organization, a project, or a repository. "
                    "The requesting user must provide a valid authentication token. "
                    "The tool returns all membership or collaboration records linked "
                    "to the specified entity identifier."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "auth_token": {
                            "type": "string",
                            "description": (
                                "Authentication token of the requesting user. "
                                "The token is validated against the system's access token registry "
                                "before any member data is returned."
                            ),
                        },
                        "entity_type": {
                            "type": "string",
                            "description": (
                                "Type of entity whose members should be listed. "
                                "Accepted values are 'organization', 'project', and 'repository'."
                            ),
                        },
                        "entity_id": {
                            "type": "string",
                            "description": (
                                "Unique identifier of the target entity. "
                                "For organizations, this corresponds to an organization identifier; "
                                "for projects, a project identifier; "
                                "and for repositories, a repository identifier."
                            ),
                        },
                    },
                    "required": ["auth_token", "entity_type", "entity_id"],
                },
            },
        }
