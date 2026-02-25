import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class RetrievePullRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: Optional[str] = None,
        search_criteria: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for pull_requests"}
            )

        project = None
        if project_id is not None:
            projects = data.get("projects", {})
            project_id_str = str(project_id)

            if project_id_str in projects:
                project_data = projects[project_id_str]
                if str(project_data.get("project_id")) == project_id_str:
                    project = project_data.copy()

            if not project:
                for project_data in projects.values():
                    if str(project_data.get("project_id")) == project_id_str:
                        project = project_data.copy()
                        break

            if not project:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Project with ID {project_id} not found",
                    }
                )

        # If search_criteria is provided, use flexible search
        if search_criteria is not None:
            if not isinstance(search_criteria, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": "search_criteria must be a dictionary",
                    }
                )

            pull_requests = data.get("pull_requests", {})
            results = []

            # Search through all pull requests
            for _pr_key, pr_data in pull_requests.items():
                if project_id is not None:
                    pr_project_id = pr_data.get("project_id")
                    if str(pr_project_id) != str(project_id):
                        continue

                match = True
                for field, value in search_criteria.items():
                    pr_value = pr_data.get(field)

                    if value is None:
                        if pr_value is not None:
                            match = False
                            break
                        continue

                    if pr_value is None:
                        match = False
                        break

                    if isinstance(value, str) and isinstance(pr_value, str):
                        if value.lower() not in pr_value.lower():
                            match = False
                            break
                    else:
                        if str(pr_value) != str(value):
                            match = False
                            break

                if match:
                    results.append(pr_data.copy())

            response = {
                "success": True,
                "count": len(results),
                "pull_requests": results,
                "search_criteria": search_criteria,
            }
            if project_id is not None:
                response["project"] = {
                    "project_id": project.get("project_id"),
                    "project_key": project.get("project_key"),
                    "project_name": project.get("project_name"),
                    "status": project.get("status"),
                    "project_owner_user_id": project.get("project_owner_user_id"),
                }
            return json.dumps(response)

        if project_id is None:
            return json.dumps(
                {
                    "success": False,
                    "error": "Either project_id or search_criteria is required",
                }
            )

        pull_requests = data.get("pull_requests", {})

        if project_id is not None:
            results = []
            for _pr_key, pr_data in pull_requests.items():
                pr_project_id = pr_data.get("project_id")
                if str(pr_project_id) == str(project_id):
                    pr = pr_data.copy()
                    results.append(pr)

            return json.dumps(
                {
                    "success": True,
                    "project": {
                        "project_id": project.get("project_id"),
                        "project_key": project.get("project_key"),
                        "project_name": project.get("project_name"),
                        "status": project.get("status"),
                        "project_owner_user_id": project.get("project_owner_user_id"),
                    },
                    "count": len(results),
                    "pull_requests": results,
                }
            )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "retrieve_pull_request",
                "description": "Retrieve pull request information for engineering traceability and PR oversight. Can query by project_id to get all PRs for a project, or use flexible search_criteria dictionary to search by any field(s) like title, source_branch, state, target_branch, author_id, repository_id, pull_request_id, etc. Returns complete PR information including state, approval_count, work_item_id, created_at, and other PR details.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The project ID to retrieve all pull requests for. If provided, returns all PRs associated with this project. (Legacy parameter, use search_criteria for flexible searching)",
                        },
                        "search_criteria": {
                            "type": "object",
                            "description": "Flexible dictionary of field-value pairs to search for pull requests. Can include any fields like title, source_branch, target_branch, state, author_id, repository_id, project_id, pull_request_id, work_item_id, etc. String fields support partial matching (case-insensitive). All criteria must match (AND logic). Example: {'title': 'payment', 'source_branch': 'feature/metrics', 'state': 'open'} or {'pull_request_id': 1}",
                            "additionalProperties": True,
                        },
                    },
                    "required": [],
                    "anyOf": [
                        {"required": ["project_id"]},
                        {"required": ["search_criteria"]},
                    ],
                },
            },
        }
