import json
import re
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpdateChangeRequest(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        pull_request_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        state: Optional[str] = None,
        work_item_id: Optional[str] = None,
        repository_id: Optional[str] = None,
        project_id: Optional[str] = None,
        author_id: Optional[str] = None,
        approval_count: Optional[int] = None,
        source_branch: Optional[str] = None,
        target_branch: Optional[str] = None,
        merged_at: Optional[str] = None,
        closed_at: Optional[str] = None,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps(
                {"success": False, "error": "Invalid data format for pull_requests"}
            )

        if pull_request_id is None:
            return json.dumps(
                {"success": False, "error": "pull_request_id is required"}
            )

        pull_requests = data.get("pull_requests", {})
        pull_request = None
        pr_key_str = str(pull_request_id)

        if pr_key_str in pull_requests:
            pr_data = pull_requests[pr_key_str]
            if str(pr_data.get("pull_request_id")) == str(pull_request_id):
                pull_request = pr_data

        if not pull_request:
            for _pr_key, pr_data in pull_requests.items():
                if str(pr_data.get("pull_request_id")) == str(pull_request_id):
                    pull_request = pr_data
                    break

        if not pull_request:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Pull request with ID {pull_request_id} not found",
                }
            )

        linked_work_item = None
        if work_item_id is not None:
            work_items = data.get("work_items", {})

            for _work_item_key, work_item_data in work_items.items():
                if str(work_item_data.get("work_item_id")) == str(work_item_id):
                    linked_work_item = work_item_data
                    break

            if not linked_work_item:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Work item with ID {work_item_id} not found",
                    }
                )

        if repository_id is not None:
            repositories = data.get("repositories", {})
            repository_exists = False

            for _repo_key, repository_data in repositories.items():
                if str(repository_data.get("repository_id")) == str(repository_id):
                    repository_exists = True
                    break

            if not repository_exists:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Repository with ID {repository_id} not found",
                    }
                )

        if project_id is not None:
            projects = data.get("projects", {})
            project = None
            project_key_str = str(project_id)

            if project_key_str in projects:
                project_data = projects[project_key_str]
                if str(project_data.get("project_id")) == str(project_id):
                    project = project_data

            if not project:
                for project_data in projects.values():
                    if str(project_data.get("project_id")) == str(project_id):
                        project = project_data
                        break

            if not project:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Project with ID {project_id} not found",
                    }
                )

        if author_id is not None:
            users = data.get("users", {})
            user_exists = False

            for _user_key, user_data in users.items():
                if str(user_data.get("user_id")) == str(author_id):
                    user_exists = True
                    break

            if not user_exists:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"User with ID {author_id} not found in users table",
                    }
                )

        if state is not None:
            valid_states = ["open", "closed", "merged", "draft"]
            if state not in valid_states:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid state '{state}'. Must be one of: {', '.join(valid_states)}",
                    }
                )

        date_format_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")

        if merged_at is not None:
            if merged_at and not date_format_pattern.match(merged_at):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid merged_at format '{merged_at}'. Must be in ISO format: YYYY-MM-DDTHH:MM:SS",
                    }
                )

        if closed_at is not None:
            if closed_at and not date_format_pattern.match(closed_at):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid closed_at format '{closed_at}'. Must be in ISO format: YYYY-MM-DDTHH:MM:SS",
                    }
                )

        # Validate state transitions and timestamp consistency
        # Determine the final state after update
        final_state = state if state is not None else pull_request.get("state")

        if state is not None and state == "merged":
            merged_at_has_value = merged_at is not None and (
                isinstance(merged_at, str) and merged_at.strip() != ""
            )
            if not merged_at_has_value and pull_request.get("merged_at") is None:
                return json.dumps(
                    {
                        "success": False,
                        "error": "merged_at timestamp is required when state is 'merged'",
                    }
                )

        if (
            merged_at is not None
            and isinstance(merged_at, str)
            and merged_at.strip() != ""
        ):
            if final_state != "merged":
                return json.dumps(
                    {
                        "success": False,
                        "error": "merged_at can only be set when state is 'merged'",
                    }
                )

        if (
            merged_at is not None
            and isinstance(merged_at, str)
            and merged_at.strip() == ""
            and final_state == "merged"
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": "Cannot clear merged_at when state is 'merged'",
                }
            )

        if approval_count is not None:
            if approval_count < 0:
                return json.dumps(
                    {
                        "success": False,
                        "error": "approval_count cannot be negative",
                    }
                )

        if source_branch is not None:
            source_branch_str = str(source_branch).strip()
            if not source_branch_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": "source_branch cannot be empty",
                    }
                )
            if len(source_branch_str) > 255:
                return json.dumps(
                    {
                        "success": False,
                        "error": "source_branch cannot exceed 255 characters",
                    }
                )

        if target_branch is not None:
            target_branch_str = str(target_branch).strip()
            if not target_branch_str:
                return json.dumps(
                    {
                        "success": False,
                        "error": "target_branch cannot be empty",
                    }
                )
            if len(target_branch_str) > 255:
                return json.dumps(
                    {
                        "success": False,
                        "error": "target_branch cannot exceed 255 characters",
                    }
                )

        if (
            title is None
            and description is None
            and state is None
            and work_item_id is None
            and repository_id is None
            and project_id is None
            and author_id is None
            and approval_count is None
            and source_branch is None
            and target_branch is None
            and merged_at is None
            and closed_at is None
        ):
            return json.dumps(
                {
                    "success": False,
                    "error": "At least one field must be provided for update",
                }
            )

        # Update fields with proper type casting
        if title is not None:
            pull_request["title"] = str(title)

        if description is not None:
            pull_request["description"] = str(description) if description else None

        if state is not None:
            pull_request["state"] = str(state)

        if work_item_id is not None:
            pull_request["work_item_id"] = str(work_item_id)

        if repository_id is not None:
            pull_request["repository_id"] = str(repository_id)

        if project_id is not None:
            pull_request["project_id"] = str(project_id)

        if author_id is not None:
            pull_request["author_id"] = str(author_id)

        if approval_count is not None:
            pull_request["approval_count"] = int(approval_count)

        if source_branch is not None:
            pull_request["source_branch"] = str(source_branch).strip()

        if target_branch is not None:
            pull_request["target_branch"] = str(target_branch).strip()

        if merged_at is not None:
            pull_request["merged_at"] = str(merged_at) if merged_at else None

        if closed_at is not None:
            pull_request["closed_at"] = str(closed_at) if closed_at else None

        # Update timestamp to system epoch
        pull_request["updated_at"] = "2026-02-11T23:59:00"

        # SOP 5: Automatic work item status updates based on PR state
        # Get the final PR state after update
        final_pr_state = state if state is not None else pull_request.get("state")
        # Get the linked work item ID (either newly linked or existing)
        linked_work_item_id = (
            work_item_id
            if work_item_id is not None
            else pull_request.get("work_item_id")
        )

        # Track the work item that was updated (for response)
        work_item_to_update = None

        if linked_work_item_id is not None:
            work_items = data.get("work_items", {})

            # Find the work item to update
            for _work_item_key, work_item_data in work_items.items():
                if str(work_item_data.get("work_item_id")) == str(linked_work_item_id):
                    work_item_to_update = work_item_data
                    break

            if work_item_to_update:
                # Rule 1: If PR is merged, automatically update work item to "done"
                if final_pr_state == "merged":
                    work_item_to_update["status"] = "done"
                    work_item_to_update["updated_at"] = "2026-02-11T23:59:00"

                # Rule 2: If PR is closed (but not merged), move work item to "blocked"
                elif final_pr_state == "closed":
                    # Only update to blocked if PR is not merged (merged_at is None)
                    if pull_request.get("merged_at") is None:
                        work_item_to_update["status"] = "blocked"
                        work_item_to_update["updated_at"] = "2026-02-11T23:59:00"

        # Cast all ID fields to strings per schema
        if pull_request.get("pull_request_id") is not None:
            pull_request["pull_request_id"] = str(pull_request.get("pull_request_id"))
        if pull_request.get("repository_id") is not None:
            pull_request["repository_id"] = str(pull_request.get("repository_id"))
        if pull_request.get("author_id") is not None:
            pull_request["author_id"] = str(pull_request.get("author_id"))
        if pull_request.get("work_item_id") is not None:
            pull_request["work_item_id"] = str(pull_request.get("work_item_id"))
        if pull_request.get("project_id") is not None:
            pull_request["project_id"] = str(pull_request.get("project_id"))
        if pull_request.get("title") is not None:
            pull_request["title"] = str(pull_request.get("title"))
        if pull_request.get("description") is not None:
            pull_request["description"] = str(pull_request.get("description"))
        if pull_request.get("state") is not None:
            pull_request["state"] = str(pull_request.get("state"))
        if pull_request.get("source_branch") is not None:
            pull_request["source_branch"] = str(pull_request.get("source_branch"))
        if pull_request.get("target_branch") is not None:
            pull_request["target_branch"] = str(pull_request.get("target_branch"))
        if pull_request.get("created_at") is not None:
            pull_request["created_at"] = str(pull_request.get("created_at"))
        if pull_request.get("updated_at") is not None:
            pull_request["updated_at"] = str(pull_request.get("updated_at"))
        if pull_request.get("merged_at") is not None:
            pull_request["merged_at"] = str(pull_request.get("merged_at"))
        if pull_request.get("closed_at") is not None:
            pull_request["closed_at"] = str(pull_request.get("closed_at"))

        response = {
            "success": True,
            "pull_request": pull_request.copy(),
        }

        work_item_for_response = None
        if linked_work_item is not None:
            # Newly linked work item
            work_item_for_response = linked_work_item
        elif work_item_to_update is not None:
            # Work item that was automatically updated
            work_item_for_response = work_item_to_update
        elif linked_work_item_id is not None:
            # Work item was already linked, find it
            work_items = data.get("work_items", {})
            for _work_item_key, work_item_data in work_items.items():
                if str(work_item_data.get("work_item_id")) == str(linked_work_item_id):
                    work_item_for_response = work_item_data
                    break

        if work_item_for_response is not None:
            work_item_info = {
                "work_item_id": str(work_item_for_response.get("work_item_id")),
                "status": str(work_item_for_response.get("status", "")),
            }
            if work_item_for_response.get("title") is not None:
                work_item_info["title"] = str(work_item_for_response.get("title"))
            if work_item_for_response.get("type") is not None:
                work_item_info["type"] = str(work_item_for_response.get("type"))
            if work_item_for_response.get("priority") is not None:
                work_item_info["priority"] = str(work_item_for_response.get("priority"))

            response["work_item"] = work_item_info

        return json.dumps(response)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_change_request",
                "description": "Update pull request information. Can update title, description, state, work_item_id (for linking orphan PRs), repository, project, author, approval count, branches, and timestamps. Use this to link orphan PRs to work items, update PR status, and manage PR metadata.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pull_request_id": {
                            "type": "string",
                            "description": "The pull request ID to update",
                        },
                        "title": {
                            "type": "string",
                            "description": "New title for the pull request",
                        },
                        "description": {
                            "type": "string",
                            "description": "New description for the pull request",
                        },
                        "state": {
                            "type": "string",
                            "description": "New state for the pull request",
                            "enum": ["open", "closed", "merged", "draft"],
                        },
                        "work_item_id": {
                            "type": "string",
                            "description": "Work item ID to link the PR to (useful for linking orphan PRs)",
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Repository ID to associate the PR with",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project ID to associate the PR with",
                        },
                        "author_id": {
                            "type": "string",
                            "description": "User ID of the PR author",
                        },
                        "approval_count": {
                            "type": "integer",
                            "description": "Number of approvals for the PR",
                        },
                        "source_branch": {
                            "type": "string",
                            "description": "Source branch name",
                        },
                        "target_branch": {
                            "type": "string",
                            "description": "Target branch name",
                        },
                        "merged_at": {
                            "type": "string",
                            "description": "Timestamp when PR was merged (ISO format: YYYY-MM-DDTHH:MM:SS)",
                        },
                        "closed_at": {
                            "type": "string",
                            "description": "Timestamp when PR was closed (ISO format: YYYY-MM-DDTHH:MM:SS)",
                        },
                    },
                    "required": ["pull_request_id"],
                },
            },
        }
