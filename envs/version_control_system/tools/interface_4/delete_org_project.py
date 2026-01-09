import json
import base64
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class DeleteOrgProject(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], project_id: str, auth_token: str) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        access_tokens = data.get("access_tokens", {})
        projects = data.get("projects", {})
        project_members = data.get("project_members", {})
        repositories = data.get("repositories", {})
        repository_collaborators = data.get("repository_collaborators", {})
        branches = data.get("branches", {})
        commits = data.get("commits", {})
        pull_requests = data.get("pull_requests", {})
        work_items = data.get("issues", {})

        deletion_log = {
            "projects": [],
            "repositories": [],
            "branches": [],
            "commits": [],
            "pull_requests": [],
            "work_items": [],
            "repository_collaborators": [],
            "project_memberships": [],
        }

        def encode(text: str) -> str:
            return base64.b64encode(text.encode("utf-8")).decode("utf-8")

        # --- Authenticate requester ---
        encoded_token = encode(auth_token)
        token_info = (
            next(
                info
                for info in access_tokens.values()
                if info.get("token_encoded") == encoded_token
            ),
            None,
        )

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

        requester_id = token_info["user_id"]

        # --- Validate project ---
        if project_id not in projects:
            return json.dumps(
                {"success": False, "error": f"Project with id {project_id} not found"}
            )

        # --- Authorization ---
        is_admin = any(
            m
            for m in project_members.values()
            if m.get("project_id") == project_id
            and m.get("user_id") == requester_id
            and m.get("roles") == "Project Administrator"
        )

        if not is_admin:
            return json.dumps(
                {
                    "success": False,
                    "error": "Access denied. Only Project Administrators can delete this project",
                }
            )

        # --- Collect repository IDs ---
        repo_ids = {
            repo_id
            for repo_id, repo in repositories.items()
            if repo.get("project_id") == project_id
        }

        # --- Work items ---
        for wid in list(work_items.keys()):
            if work_items[wid].get("project_id") == project_id:
                deletion_log["work_items"].append(wid)
                del work_items[wid]

        # --- Pull requests ---
        for pr_id in list(pull_requests.keys()):
            if pull_requests[pr_id].get("repository_id") in repo_ids:
                deletion_log["pull_requests"].append(pr_id)
                del pull_requests[pr_id]

        # --- Commits ---
        for commit_id in list(commits.keys()):
            if commits[commit_id].get("repository_id") in repo_ids:
                deletion_log["commits"].append(commit_id)
                del commits[commit_id]

        # --- Branches ---
        for branch_id in list(branches.keys()):
            if branches[branch_id].get("repository_id") in repo_ids:
                deletion_log["branches"].append(branch_id)
                del branches[branch_id]

        # --- Repository collaborators ---
        for collab_id in list(repository_collaborators.keys()):
            if repository_collaborators[collab_id].get("repository_id") in repo_ids:
                deletion_log["repository_collaborators"].append(collab_id)
                del repository_collaborators[collab_id]

        # --- Repositories ---
        for repo_id in list(repositories.keys()):
            if repo_id in repo_ids:
                deletion_log["repositories"].append(repo_id)
                del repositories[repo_id]

        # --- Project memberships ---
        for membership_id in list(project_members.keys()):
            if project_members[membership_id].get("project_id") == project_id:
                deletion_log["project_memberships"].append(membership_id)
                del project_members[membership_id]

        # --- Project ---
        deletion_log["projects"].append(project_id)
        del projects[project_id]

        # --- Summary ---
        summary = {k: len(v) for k, v in deletion_log.items()}

        return json.dumps(
            {
                "success": True,
                "message": "Project and all related entities deleted successfully",
                "project_id": project_id,
                "summary": summary,
                "deleted_entities": deletion_log,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "delete_org_project",
                "description": (
                    "Deletes a project and all associated entities. "
                    "Returns a detailed log of every deleted entity grouped by type."
                    "The user must be a Project Administrator."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The unique identifier of the project to delete.",
                        },
                        "auth_token": {
                            "type": "string",
                            "description": "Authentication token of the requesting Project Administrator.",
                        },
                    },
                    "required": ["project_id", "auth_token"],
                },
            },
        }
