import json
from typing import Any, Dict, Optional, Union
from tau_bench.envs.tool import Tool


class FetchEntityInfo(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        entity_type: str,
        repository_id: str,
        entity_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        branch_id: Optional[str] = None,
        author_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
        status: Optional[str] = None,
        is_default: Optional[bool] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not entity_type:
            return json.dumps({"success": False, "error": "entity_type is required"})
        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required"})

        # Validate entity_type
        valid_entity_types = ["branch", "commit", "issue", "workflow", "label", "directory"]
        if entity_type not in valid_entity_types:
            return json.dumps({"success": False, "error": f"Invalid entity_type '{entity_type}'. Valid values: branch, commit, issue, workflow, label, directory"})

        # Parse filters if it's a string
        if filters is not None:
            if isinstance(filters, str):
                try:
                    filters = json.loads(filters)
                except json.JSONDecodeError:
                    return json.dumps({"success": False, "error": "filters must be a valid JSON object"})
        else:
            filters = {}

        repositories = data.get("repositories", {})

        # Validate repository exists
        if str(repository_id) not in repositories:
            return json.dumps({"success": False, "error": f"Repository with id '{repository_id}' not found"})

        # Get the appropriate data table based on entity_type
        entity_table_map = {
            "branch": "branches",
            "commit": "commits",
            "issue": "issues",
            "workflow": "workflows",
            "label": "labels",
            "directory": "directories"
        }

        entity_id_field_map = {
            "branch": "branch_id",
            "commit": "commit_id",
            "issue": "issue_id",
            "workflow": "workflow_id",
            "label": "label_id",
            "directory": "directory_id"
        }

        table_name = entity_table_map[entity_type]
        id_field = entity_id_field_map[entity_type]
        entities = data.get(table_name, {})

        # If entity_id is provided, fetch specific entity
        if entity_id is not None:
            if str(entity_id) not in entities:
                return json.dumps({"success": False, "error": f"{entity_type.capitalize()} with id '{entity_id}' not found"})

            entity = entities[str(entity_id)]

            # Validate entity belongs to the repository
            if str(entity.get("repository_id")) != str(repository_id):
                return json.dumps({"success": False, "error": f"{entity_type.capitalize()} with id '{entity_id}' does not belong to repository '{repository_id}'"})

            return json.dumps({"success": True, "result": entity})

        # Search for entities matching filters
        results = []

        for ent_id, entity in entities.items():
            # Filter by repository_id
            if str(entity.get("repository_id")) != str(repository_id):
                continue

            # Apply entity-specific optional parameters
            if entity_type == "branch":
                if is_default is not None and entity.get("is_default") != is_default:
                    continue

            if entity_type in ["commit", "issue"]:
                if author_id is not None and str(entity.get("author_id")) != str(author_id):
                    continue

            if entity_type == "issue":
                if assignee_id is not None and str(entity.get("assignee_id")) != str(assignee_id):
                    continue
                if status is not None and entity.get("status") != status:
                    continue

            if entity_type == "workflow":
                if status is not None and entity.get("status") != status:
                    continue

            if entity_type == "directory":
                if branch_id is not None and str(entity.get("branch_id")) != str(branch_id):
                    continue

            # Apply generic filters from filters dict
            match = True
            for filter_key, filter_value in filters.items():
                entity_value = entity.get(filter_key)
                if entity_value is None:
                    match = False
                    break
                if str(entity_value) != str(filter_value):
                    match = False
                    break

            if match:
                results.append(entity)

        return json.dumps({"success": True, "result": results})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fetch_entity_info",
                "description": "Fetches entity information based on entity type. Supports fetching a specific entity by ID or searching with filters. Supported entity types: branch, commit, issue, workflow, label, directory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entity_type": {
                            "type": "string",
                            "description": "The type of entity to fetch. Valid values: branch, commit, issue, workflow, label, directory."
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository to search in."
                        },
                        "entity_id": {
                            "type": "string",
                            "description": "The unique identifier of the specific entity to fetch. If provided, returns that entity directly (optional)."
                        },
                        "filters": {
                            "type": "object",
                            "description": "A dictionary of field-value pairs to filter entities. Any field from the entity can be used. Any filter provided should exist in the respective entity schema (optional)."
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "Filter by branch ID. Applicable for entity_type: directory (optional)."
                        },
                        "author_id": {
                            "type": "string",
                            "description": "Filter by author ID. Applicable for entity_type: commit, issue (optional)."
                        },
                        "assignee_id": {
                            "type": "string",
                            "description": "Filter by assignee ID. Applicable for entity_type: issue (optional)."
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status. Applicable for entity_type: issue (open, closed, in_progress), workflow (active, disabled, deleted) (optional)."
                        },
                        "is_default": {
                            "type": "boolean",
                            "description": "Filter by default branch flag. Applicable for entity_type: branch (optional)."
                        }
                    },
                    "required": ["entity_type", "repository_id"]
                }
            }
        }
