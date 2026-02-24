import json
import random
import string
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class AddCommit(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        branch_id: str,
        file_path: str,
        file_name: str,
        new_content: str,
        author_id: str,
        commit_message: str,
        commit_type: Optional[str] = None,
        ticket_id: Optional[str] = None,
    ) -> str:
        timestamp = "2026-02-02 23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        def generate_commit_sha() -> str:
            return "".join(random.choices(string.hexdigits.lower(), k=40))

        def find_file(
            files_dict: Dict[str, Any],
            repository_id_str: str,
            branch_id_str: str,
            file_path_str: str,
            file_name_str: str,
        ) -> Optional[tuple]:
            for fid, file in files_dict.items():
                if not isinstance(file, dict):
                    continue
                if (
                    str(file.get("repository_id")) == repository_id_str
                    and str(file.get("branch_id")) == branch_id_str
                    and str(file.get("file_path", "")).strip() == file_path_str
                    and str(file.get("file_name", "")).strip() == file_name_str
                ):
                    return str(fid), file
            return None, None

        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required"})

        if not branch_id:
            return json.dumps({"success": False, "error": "branch_id is required"})

        if not file_path:
            return json.dumps({"success": False, "error": "file_path is required"})

        if not file_name:
            return json.dumps({"success": False, "error": "file_name is required"})

        if not new_content:
            return json.dumps({"success": False, "error": "new_content is required"})

        if not author_id:
            return json.dumps({"success": False, "error": "author_id is required"})

        if not commit_message:
            return json.dumps({"success": False, "error": "commit_message is required"})

        repositories_dict = data.get("repositories", {})
        branches_dict = data.get("branches", {})
        files_dict = data.get("files", {})
        commits_dict = data.get("commits", {})
        users_dict = data.get("users", {})
        tickets_dict = data.get("tickets", {})

        repository_id_str = str(repository_id).strip()
        branch_id_str = str(branch_id).strip()
        file_path_str = str(file_path).strip()
        file_name_str = str(file_name).strip()
        new_content_str = str(new_content).strip()
        author_id_str = str(author_id).strip()
        commit_message_str = str(commit_message).strip()
        commit_type_str = str(commit_type).strip() if commit_type else None
        ticket_id_str = str(ticket_id).strip() if ticket_id else None

        if not file_path_str:
            return json.dumps({"success": False, "error": "File path cannot be empty"})

        if not file_name_str:
            return json.dumps({"success": False, "error": "File name cannot be empty"})

        if not new_content_str:
            return json.dumps(
                {"success": False, "error": "File content cannot be empty"}
            )

        if not commit_message_str:
            return json.dumps(
                {"success": False, "error": "Commit message cannot be empty"}
            )

        if commit_type_str:
            valid_commit_types = ["fix", "feat", "chore"]

            if commit_type_str not in valid_commit_types:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid commit_type '{commit_type_str}'. Must be one of: {', '.join(valid_commit_types)}",
                    }
                )

        if repository_id_str not in repositories_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Repository with ID '{repository_id_str}' not found",
                }
            )

        repository = repositories_dict[repository_id_str]

        if not isinstance(repository, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid repository data structure for repository ID '{repository_id_str}'",
                }
            )

        if branch_id_str not in branches_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Branch with ID '{branch_id_str}' not found",
                }
            )

        branch = branches_dict[branch_id_str]

        if not isinstance(branch, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid branch data structure for branch ID '{branch_id_str}'",
                }
            )

        branch_repo_id = str(branch.get("repository_id", "")).strip()
        if branch_repo_id != repository_id_str:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Branch '{branch_id_str}' does not belong to repository '{repository_id_str}'",
                }
            )

        if author_id_str not in users_dict:
            return json.dumps(
                {"success": False, "error": f"User with ID '{author_id_str}' not found"}
            )

        author = users_dict[author_id_str]

        if not isinstance(author, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid user data structure for author ID '{author_id_str}'",
                }
            )

        author_status = author.get("status")
        if author_status != "active":
            return json.dumps(
                {
                    "success": False,
                    "error": f"User '{author_id_str}' is not active and cannot create commits",
                }
            )

        if ticket_id_str:
            if ticket_id_str not in tickets_dict:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Ticket with ID '{ticket_id_str}' not found",
                    }
                )

            ticket = tickets_dict[ticket_id_str]

            if not isinstance(ticket, dict):
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid ticket data structure for ticket ID '{ticket_id_str}'",
                    }
                )

        file_id_str, existing_file = find_file(
            files_dict, repository_id_str, branch_id_str, file_path_str, file_name_str
        )

        commit_sha = generate_commit_sha()
        new_commit_id = generate_id(commits_dict)

        new_commit = {
            "commit_id": str(new_commit_id),
            "repository_id": str(repository_id_str),
            "branch_id": str(branch_id_str),
            "commit_sha": str(commit_sha),
            "author_id": str(author_id_str),
            "commit_message": str(commit_message_str),
            "commit_type": str(commit_type_str),
            "ticket_id": str(ticket_id_str),
            "committed_at": timestamp,
            "created_at": timestamp,
        }

        commits_dict[new_commit_id] = new_commit

        if file_id_str and existing_file:
            existing_file["content"] = new_content_str
            existing_file["last_commit_id"] = new_commit_id
            existing_file["updated_at"] = timestamp

            file_return = existing_file.copy()
            file_return["file_id"] = file_id_str
            action = "updated"
        else:
            new_file_id = generate_id(files_dict)
            new_file = {
                "file_id": new_file_id,
                "repository_id": str(repository_id_str),
                "branch_id": str(branch_id_str),
                "file_path": str(file_path_str),
                "file_name": str(file_name_str),
                "content": str(new_content_str),
                "last_commit_id": str(new_commit_id),
                "created_at": timestamp,
                "updated_at": timestamp,
            }

            files_dict[new_file_id] = new_file

            file_return = new_file.copy()
            file_id_str = str(new_file_id)
            action = "created"

        branch["commit_sha"] = commit_sha
        branch["updated_at"] = timestamp

        commit_return = new_commit.copy()
        commit_return["author_email"] = str(author.get("email"))
        commit_return["author_name"] = str(
            f"{author.get('first_name', '')} {author.get('last_name', '')}".strip()
        )
        commit_return["branch_name"] = str(branch.get("branch_name"))
        commit_return["repository_name"] = str(repository.get("repository_name"))

        if ticket_id_str and ticket_id_str in tickets_dict:
            commit_return["ticket_number"] = str(tickets_dict[ticket_id_str].get(
                "ticket_number"
            ))

        message = f"Commit {commit_sha[:7]} created successfully: '{commit_message_str}' - File '{file_name_str}' {action} in branch '{branch.get('branch_name')}'"

        return json.dumps(
            {
                "success": True,
                "commit": commit_return,
                "file": file_return,
                "action": action,
                "message": message,
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_commit",
                "description": (
                    "Applies changes to a file within a branch and creates a commit to record the modification. "
                    "This function updates existing files or creates new files with specified content, then commits the changes. "
                    "Use this to implement code fixes for identified bugs, apply corrections to resolve ticket issues, "
                    "update configuration files, modify documentation, or make any code changes needed to address support tickets. "
                    "Each commit creates a permanent record of the change with a message describing what was modified and why."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository containing the file.",
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "The unique identifier of the branch where the change will be committed.",
                        },
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file within the repository (including directory structure).",
                        },
                        "file_name": {
                            "type": "string",
                            "description": "The name of the file to update or create.",
                        },
                        "new_content": {
                            "type": "string",
                            "description": "The new content for the file after applying the fix or changes.",
                        },
                        "author_id": {
                            "type": "string",
                            "description": "The unique identifier of the user creating the commit.",
                        },
                        "commit_message": {
                            "type": "string",
                            "description": "A descriptive message explaining what changes were made and why.",
                        },
                        "commit_type": {
                            "type": "string",
                            "description": "Optional. The type of commit following conventional commits",
                            "enum": ["fix", "feat", "chore"],
                        },
                        "ticket_id": {
                            "type": "string",
                            "description": "Optional. The unique identifier of the ticket this commit addresses for traceability.",
                        },
                    },
                    "required": [
                        "repository_id",
                        "branch_id",
                        "file_path",
                        "file_name",
                        "new_content",
                        "author_id",
                        "commit_message",
                    ],
                },
            },
        }
