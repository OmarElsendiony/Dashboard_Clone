import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class GetBranchDetails(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        branch_id: Optional[str] = None,
        repository_id: Optional[str] = None,
        branch_name: Optional[str] = None,
    ) -> str:
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return json.dumps({"success": bool(False), "error": str("Wrong data format")})
        if not isinstance(data, dict):
            return json.dumps({"success": bool(False), "error": str("Wrong data format")})

        if not any([branch_id, branch_name]):
            return json.dumps(
                {
                    "success": bool(False),
                    "error": str("At least one parameter must be provided: branch_id or branch_name"),
                }
            )

        if branch_name is not None and not str(branch_name).strip():
            return json.dumps(
                {
                    "success": bool(False),
                    "error": str("branch_name must be non-empty when provided"),
                }
            )

        if branch_name and not repository_id:
            return json.dumps(
                {
                    "success": bool(False),
                    "error": str("repository_id must be provided when using branch_name"),
                }
            )

        if branch_id and (branch_name or repository_id):
            return json.dumps(
                {
                    "success": bool(False),
                    "error": str("Provide either branch_id alone or branch_name with repository_id, not both"),
                }
            )

        branches = data.get("branches", {})

        target_branch = None

        if branch_id:
            branch_id_str = str(branch_id).strip()
            if not branch_id_str:
                return json.dumps(
                    {"success": bool(False), "error": str("branch_id must be non-empty when provided")}
                )
            if branch_id_str in branches:
                target_branch = branches[branch_id_str]
            else:
                return json.dumps(
                    {
                        "success": bool(False),
                        "error": str(f"Branch with id '{branch_id}' not found"),
                    }
                )
        else:
            repositories = data.get("repositories", {})
            repo_id_str = str(repository_id).strip()
            if repo_id_str not in repositories:
                return json.dumps(
                    {
                        "success": bool(False),
                        "error": str(f"Repository with id '{repository_id}' not found"),
                    }
                )

            branch_name_lower = str(branch_name).strip().lower()
            for branch in branches.values():
                if str(branch.get("repository_id")) != repo_id_str:
                    continue
                db_branch_name_lower = str(branch.get("branch_name") or "").lower()
                if db_branch_name_lower == branch_name_lower:
                    target_branch = branch
                    break

            if not target_branch:
                return json.dumps(
                    {
                        "success": bool(False),
                        "error": str(f"Branch '{branch_name}' not found in repository '{repository_id}'"),
                    }
                )

        raw = target_branch
        branch_out = {
            "branch_id": str(raw.get("branch_id", "")),
            "repository_id": str(raw.get("repository_id", "")),
            "branch_name": str(raw.get("branch_name", "")),
            "source_branch_name": str(raw["source_branch_name"]) if raw.get("source_branch_name") is not None else None,
            "commit_sha": str(raw.get("commit_sha", "")),
            "linked_ticket_id": str(raw["linked_ticket_id"]) if raw.get("linked_ticket_id") is not None else None,
            "created_by": str(raw["created_by"]) if raw.get("created_by") is not None else None,
            "status": str(raw.get("status", "")),
            "created_at": str(raw.get("created_at", "")),
            "updated_at": str(raw.get("updated_at", "")),
        }

        return json.dumps({"success": bool(True), "branch": branch_out})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_branch_details",
                "description": "Returns detailed information about a specific branch by branch id or by branch name and repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "branch_id": {
                            "type": "string",
                            "description": "Branch identifier. Use this alone to fetch by id.",
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Repository identifier. Required when identifying the branch by name.",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "Branch name (matched case-insensitively). Use with repository_id to fetch by name.",
                        },
                    },
                    "required": [],
                    "oneOf": [
                        {"required": ["branch_id"]},
                        {"required": ["branch_name", "repository_id"]},
                    ],
                },
            },
        }
