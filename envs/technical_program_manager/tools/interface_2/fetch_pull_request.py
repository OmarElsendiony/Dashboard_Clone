import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class FetchPullRequest(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'data' must be a dict"
            })

        if not repository_id and not project_id:
            return json.dumps({
                "success": False,
                "error": "Either 'repository_id' or 'project_id' must be provided"
            })

        prs_dict = data.get("pull_requests", {})
        repos_dict = data.get("repositories", {})
        projects_dict = data.get("projects", {})

        if not isinstance(prs_dict, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format: 'pull_requests' must be a dict"
            })

        if repository_id is not None:

            repository_id_clean = str(repository_id).strip()

            if isinstance(repos_dict, dict) and repos_dict:
                if repository_id_clean not in [str(rid) for rid in repos_dict.keys()]:
                    return json.dumps({
                        "success": False,
                        "error": "Repository not found for given repository_id"
                    })

            open_prs = []
            merged_prs = []
            closed_prs = []
            draft_prs = []

            for pr_id, pr in prs_dict.items():

                if str(pr.get("repository_id")) != repository_id_clean:
                    continue

                pr_obj = {
                    "pr_id": str(pr_id),
                    "title": str(pr.get("title", "")),
                    "state": str(pr.get("state", "")),
                    "repository_id": str(pr.get("repository_id", "")),
                    "project_id": str(pr.get("project_id", "")),
                    "work_item_id": str(pr.get("work_item_id", "")),
                    "created_at": str(pr.get("created_at", "")),
                    "updated_at": str(pr.get("updated_at", "")),
                }

                state = pr_obj["state"]

                if state == "open":
                    open_prs.append(pr_obj)
                elif state == "merged":
                    merged_prs.append(pr_obj)
                elif state == "closed":
                    closed_prs.append(pr_obj)
                else:
                    draft_prs.append(pr_obj)

            if not open_prs and not merged_prs and not closed_prs and not draft_prs:
                return json.dumps({
                    "success": False,
                    "error": "No pull requests found for the given repository_id"
                })

            return json.dumps({
                "success": True,
                "mode": "repository",
                "repository_id": repository_id_clean,
                "pull_requests": {
                    "open": open_prs,
                    "merged": merged_prs,
                    "closed": closed_prs,
                    "draft": draft_prs
                }
            })

        if project_id is not None:

            project_id_clean = str(project_id).strip()

            if isinstance(projects_dict, dict) and projects_dict:
                if project_id_clean not in [str(pid) for pid in projects_dict.keys()]:
                    return json.dumps({
                        "success": False,
                        "error": "Project not found for given project_id"
                    })

            matched_prs = []

            for pr_id, pr in prs_dict.items():

                if str(pr.get("project_id")) != project_id_clean:
                    continue

                pr_obj = {
                    "pr_id": str(pr_id),
                    "title": str(pr.get("title", "")),
                    "state": str(pr.get("state", "")),
                    "repository_id": str(pr.get("repository_id", "")),
                    "project_id": str(pr.get("project_id", "")),
                }

                matched_prs.append(pr_obj)

            if not matched_prs:
                return json.dumps({
                    "success": False,
                    "error": "No pull requests found for the given project_id"
                })

            closed_merged_count = sum(
                1 for pr in matched_prs if pr["state"] in ["closed", "merged"]
            )

            remaining_count = sum(
                1 for pr in matched_prs if pr["state"] not in ["closed", "merged"]
            )

            return json.dumps({
                "success": True,
                "mode": "project",
                "project_id": project_id_clean,
                "pull_requests": matched_prs,
                "closed_or_merged_prs": closed_merged_count,
                "remaining_prs": remaining_count
            })

    @staticmethod 
    def get_info() -> Dict[str, Any]:
        return { 
            "type": "function",
            "function": { 
                "name": "fetch_pull_request", 
                "description": "Retrieves pull requests associated with a repository or a project. "
                "Use this tool to review pull requests created during project implementation, "
                "validate completion progress before project closure, or track development activity within a specific repository.",
                "parameters": { 
                    "type": "object",
                    "properties": { 
                        "repository_id": { 
                            "type": "string", 
                            "description": "The unique identifier of the repository."
                        }, 
                        "project_id": {
                            "type": "string", 
                            "description": "Unique identifier that represents the project."
                            } 
                        }, 
                        "required": [],
                        "oneOf": [
                            {"required": ["repository_id"]}, 
                            {"required": ["project_id"]}, 
                        ] 
                    }
                } 
            }