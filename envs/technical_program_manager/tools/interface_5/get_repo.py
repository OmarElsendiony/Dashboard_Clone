import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetRepo(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: Optional[str] = None,
        project_id: Optional[str] = None,
        filter_criteria: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for repositories"}
            )

        if repository_id is None and project_id is None and filter_criteria is None:
            return json.dumps(
                {
                    "success": False,
                    "error": "Either repository_id, project_id, or filter_criteria is required",
                }
            )

        repositories = data.get("repositories", {})
        projects = data.get("projects", {})

        def normalize_repository(repo_data: Dict[str, Any]) -> Dict[str, Any]:
            """Helper function to normalize repository fields to strings"""
            normalized = repo_data.copy()
            if normalized.get("repository_id") is not None:
                normalized["repository_id"] = str(normalized.get("repository_id"))
            if normalized.get("project_id") is not None:
                normalized["project_id"] = str(normalized.get("project_id"))
            if normalized.get("repository_name") is not None:
                normalized["repository_name"] = str(normalized.get("repository_name"))
            if normalized.get("description") is not None:
                normalized["description"] = str(normalized.get("description"))
            if normalized.get("default_branch") is not None:
                normalized["default_branch"] = str(normalized.get("default_branch"))
            if normalized.get("created_at") is not None:
                normalized["created_at"] = str(normalized.get("created_at"))
            if normalized.get("updated_at") is not None:
                normalized["updated_at"] = str(normalized.get("updated_at"))
            return normalized

        # Validate repository_id if provided
        validated_repository = None
        if repository_id is not None:
            repository_id_str = str(repository_id)
            if repository_id_str in repositories:
                repository_data = repositories[repository_id_str]
                if str(repository_data.get("repository_id")) == repository_id_str:
                    validated_repository = repository_data.copy()

            if not validated_repository:
                for _repo_key, repository_data in repositories.items():
                    if str(repository_data.get("repository_id")) == repository_id_str:
                        validated_repository = repository_data.copy()
                        break

            if not validated_repository:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Repository with ID {repository_id} not found",
                    }
                )

        # Validate project_id if provided
        validated_project = None
        if project_id is not None:
            project_id_str = str(project_id)
            if project_id_str in projects:
                project_data = projects[project_id_str]
                if str(project_data.get("project_id")) == project_id_str:
                    validated_project = project_data.copy()

            if not validated_project:
                for project_data in projects.values():
                    if str(project_data.get("project_id")) == project_id_str:
                        validated_project = project_data.copy()
                        break

            if not validated_project:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Project with ID {project_id} not found",
                    }
                )

        # If repository_id is provided, return that specific repository
        if repository_id is not None:
            normalized_repo = normalize_repository(validated_repository)
            return json.dumps(
                {
                    "success": True,
                    "repository": normalized_repo,
                }
            )

        # If filter_criteria is provided, use flexible search
        if filter_criteria is not None:
            if not isinstance(filter_criteria, dict):
                return json.dumps(
                    {"success": False, "error": "filter_criteria must be a dictionary"}
                )

            # Convert dictionary to list first
            all_repositories = [repo_data.copy() for repo_data in repositories.values()]
            results = []

            # Search through all repositories
            for repository_data in all_repositories:
                # If repository_id is provided, filter by repository_id first
                if repository_id is not None:
                    repo_id = repository_data.get("repository_id")
                    if str(repo_id) != str(repository_id):
                        continue

                # If project_id is provided, filter by project_id first
                if project_id is not None:
                    repo_project_id = repository_data.get("project_id")
                    if str(repo_project_id) != str(project_id):
                        continue

                match = True
                for field, value in filter_criteria.items():
                    repo_value = repository_data.get(field)

                    if value is None:
                        if repo_value is not None:
                            match = False
                            break
                        continue

                    if repo_value is None:
                        match = False
                        break

                    # Handle string comparison (case-insensitive partial matching)
                    if isinstance(value, str) and isinstance(repo_value, str):
                        if value.lower() not in repo_value.lower():
                            match = False
                            break
                    # Handle exact match (including string/number conversion for IDs)
                    else:
                        if str(repo_value) != str(value):
                            match = False
                            break

                if match:
                    normalized_repo = normalize_repository(repository_data)
                    results.append(normalized_repo)

            response = {
                "success": True,
                "count": len(results),
                "repositories": results,
                "filter_criteria": filter_criteria,
            }
            if project_id is not None:
                response["project_id"] = str(project_id)
            return json.dumps(response)

        # Legacy behavior: use project_id
        if project_id is not None:
            results = []
            for _repo_key, repository_data in repositories.items():
                if str(repository_data.get("project_id")) == str(project_id):
                    normalized_repo = normalize_repository(repository_data)
                    results.append(normalized_repo)

            return json.dumps(
                {
                    "success": True,
                    "project_id": str(project_id),
                    "count": len(results),
                    "repositories": results,
                }
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_repo",
                "description": "Retrieve repository information. Can query by repository_id to get a specific repository, by project_id to get all repositories for a project, or use flexible filter_criteria dictionary to search by any field(s) like repository_name, description, default_branch, project_id, etc. If repository_id is provided, project_id and filter_criteria are ignored. Returns complete repository information including repository name, description, default branch, associated project, and timestamps. Use this to access repository details for code management, branch tracking, and repository lifecycle management.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The repository ID to retrieve information for. If provided, returns that specific repository. (Legacy parameter, use filter_criteria for flexible searching)",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "The project ID to retrieve all repositories for. If provided, returns all repositories associated with this project. Ignored if repository_id is provided. (Legacy parameter, use filter_criteria for flexible searching)",
                        },
                        "filter_criteria": {
                            "type": "object",
                            "description": "Flexible dictionary of field-value pairs to search for repositories. Can include any fields like repository_name, description, default_branch, project_id, repository_id, etc. String fields support partial matching (case-insensitive). All criteria must match (AND logic). Example: {'repository_name': 'backend', 'default_branch': 'main'} or {'project_id': '21'}",
                            "additionalProperties": True,
                        },
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["repository_id"]},
                        {"required": ["project_id"]},
                        {"required": ["filter_criteria"]},
                    ],
                },
            },
        }
