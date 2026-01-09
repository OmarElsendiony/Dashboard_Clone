import json
import hashlib
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ForkRepo(Tool):
    """Tool for forking (cloning) a repository into a new namespace in the version control system."""

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        source_repo_id: str,
        new_owner_email: str,
        new_repo_name: str,
    ) -> str:
        """
        Fork (clone) a repository into a new namespace.

        Args:
            data: The data dictionary containing all version control system data.
            source_repo_id: The ID of the source repository to fork (required).
            new_owner_email: The email of the user who will own the forked repository (required).
            new_repo_name: The name of the new forked repository (required, must be unique).

        Returns:
            str: A JSON-encoded string containing the success status and forked repository data.
        """

        def generate_id(table: Dict[str, Any]) -> str:
            """
            Generates a new unique ID for a record.

            Returns:
                str: The new unique ID as a string.
            """
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)

        def generate_commit_sha(repo_name: str, branch_name: str, timestamp: str, suffix: str = "") -> str:
            """
            Generates a unique commit SHA for a branch.

            Returns:
                str: A 40-character hexadecimal SHA string.
            """
            content = f"{repo_name}:{branch_name}:{timestamp}:{suffix}"
            return hashlib.sha1(content.encode()).hexdigest()

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})
        users = data.get("users", {})
        branches = data.get("branches", {})
        repository_collaborators = data.get("repository_collaborators", {})
        directories = data.get("directories", {})
        files = data.get("files", {})
        file_contents = data.get("file_contents", {})

        # Validate required fields
        if not source_repo_id:
            return json.dumps({"success": False, "error": "Missing required parameter: source_repo_id"})

        if not new_owner_email:
            return json.dumps({"success": False, "error": "Missing required parameter: new_owner_email"})

        if not new_repo_name:
            return json.dumps({"success": False, "error": "Missing required parameter: new_repo_name"})

        if not isinstance(new_repo_name, str) or not new_repo_name.strip():
            return json.dumps({"success": False, "error": "new_repo_name must be a non-empty string"})

        new_repo_name = new_repo_name.strip()
        source_repo_id = str(source_repo_id).strip()

        # Validate source repository exists
        if source_repo_id not in repositories:
            return json.dumps({
                "success": False,
                "error": f"Source repository with ID '{source_repo_id}' not found"
            })

        source_repo = repositories[source_repo_id]

        # Check if source repository is archived
        if source_repo.get("is_archived"):
            return json.dumps({
                "success": False,
                "error": f"Cannot fork archived repository '{source_repo.get('repository_name')}'"
            })

        # Find new owner by email
        new_owner = None
        new_owner_id = None
        for user_id, user in users.items():
            if user.get("email") == new_owner_email:
                new_owner = user
                new_owner_id = user_id
                break

        if not new_owner:
            return json.dumps({
                "success": False,
                "error": f"User with email '{new_owner_email}' not found"
            })

        # Check if new owner is active
        if new_owner.get("status") != "active":
            return json.dumps({
                "success": False,
                "error": f"User '{new_owner_email}' is not active"
            })

        # Check if new repository name already exists
        for _, repo in repositories.items():
            if repo.get("repository_name") == new_repo_name:
                return json.dumps({
                    "success": False,
                    "error": f"Repository with name '{new_repo_name}' already exists"
                })

        # Set timestamp for created_at and updated_at
        timestamp = "2026-01-01T23:59:00"

        # Generate new repository ID
        new_repo_id = generate_id(repositories)

        # Create new forked repository record
        new_repo = {
            "repository_id": new_repo_id,
            "owner_type": "user",
            "owner_id": new_owner_id,
            "repository_name": new_repo_name,
            "description": source_repo.get("description", ""),
            "default_branch": source_repo.get("default_branch", "main"),
            "is_fork": True,
            "parent_repository_id": source_repo_id,
            "is_archived": False,
            "forks_count": 0,
            "license_type": source_repo.get("license_type", "unlicensed"),
            "created_at": timestamp,
            "updated_at": timestamp,
            "pushed_at": timestamp,
        }

        # Add the new repository to the repositories dictionary
        repositories[new_repo_id] = new_repo

        # Increment forks_count on the parent repository
        source_repo["forks_count"] = source_repo.get("forks_count", 0) + 1
        source_repo["updated_at"] = timestamp

        # Copy branches from source repository to the new forked repository
        # Build mapping from old branch_id to new branch_id
        branch_id_mapping = {}  # old_branch_id -> new_branch_id
        new_branches = []

        for branch_id, branch in branches.items():
            if branch.get("repository_id") == source_repo_id:
                new_branch_id = generate_id(branches)
                branch_id_mapping[branch_id] = new_branch_id
                branch_name = branch.get("branch_name")

                new_branch = {
                    "branch_id": new_branch_id,
                    "repository_id": new_repo_id,
                    "branch_name": branch_name,
                    "commit_sha": generate_commit_sha(new_repo_name, branch_name, timestamp, f"fork-{branch.get('commit_sha', '')[:8]}"),
                    "source_branch": None if branch.get("is_default") else branch.get("source_branch"),
                    "is_default": branch.get("is_default", False),
                    "created_at": timestamp,
                    "updated_at": timestamp,
                }

                branches[new_branch_id] = new_branch
                new_branches.append(new_branch)

        # Copy directories from source repository
        # Build mapping from old directory_id to new directory_id
        directory_id_mapping = {}  # old_directory_id -> new_directory_id
        new_directories = []

        # First pass: collect all source directories
        source_directories = []
        for dir_id, directory in directories.items():
            if directory.get("repository_id") == source_repo_id:
                source_directories.append((dir_id, directory))

        # Sort by directory path length to process parents before children
        source_directories.sort(key=lambda x: len(x[1].get("directory_path", "")))

        for old_dir_id, directory in source_directories:
            new_dir_id = generate_id(directories)
            directory_id_mapping[old_dir_id] = new_dir_id

            old_branch_id = directory.get("branch_id")
            new_branch_id = branch_id_mapping.get(old_branch_id, old_branch_id)

            old_parent_dir_id = directory.get("parent_directory_id")
            new_parent_dir_id = directory_id_mapping.get(old_parent_dir_id) if old_parent_dir_id else None

            new_directory = {
                "directory_id": new_dir_id,
                "repository_id": new_repo_id,
                "branch_id": new_branch_id,
                "directory_path": directory.get("directory_path"),
                "parent_directory_id": new_parent_dir_id,
                "created_at": timestamp,
                "updated_at": timestamp,
            }

            directories[new_dir_id] = new_directory
            new_directories.append(new_directory)

        # Copy files from source repository
        # Build mapping from old file_id to new file_id
        file_id_mapping = {}  # old_file_id -> new_file_id
        new_files = []

        for file_id, file_record in files.items():
            if file_record.get("repository_id") == source_repo_id:
                new_file_id = generate_id(files)
                file_id_mapping[file_id] = new_file_id

                old_branch_id = file_record.get("branch_id")
                new_branch_id = branch_id_mapping.get(old_branch_id, old_branch_id)

                old_dir_id = file_record.get("directory_id")
                new_dir_id = directory_id_mapping.get(old_dir_id, old_dir_id)

                new_file = {
                    "file_id": new_file_id,
                    "repository_id": new_repo_id,
                    "branch_id": new_branch_id,
                    "directory_id": new_dir_id,
                    "file_path": file_record.get("file_path"),
                    "file_name": file_record.get("file_name"),
                    "language": file_record.get("language"),
                    "is_binary": file_record.get("is_binary", False),
                    "last_modified_at": timestamp,
                    "last_commit_id": file_record.get("last_commit_id"),
                    "created_at": timestamp,
                    "updated_at": timestamp,
                }

                files[new_file_id] = new_file
                new_files.append(new_file)

        # Copy file contents for the copied files
        new_file_contents = []

        for content_id, content_record in file_contents.items():
            old_file_id = content_record.get("file_id")
            if old_file_id in file_id_mapping:
                new_content_id = generate_id(file_contents)
                new_file_id = file_id_mapping[old_file_id]

                new_content = {
                    "content_id": new_content_id,
                    "file_id": new_file_id,
                    "commit_id": content_record.get("commit_id"),
                    "content": content_record.get("content"),
                    "encoding": content_record.get("encoding", "utf-8"),
                    "created_at": timestamp,
                }

                file_contents[new_content_id] = new_content
                new_file_contents.append(new_content)

        # Add the new owner as an admin collaborator
        new_collaborator_id = generate_id(repository_collaborators)

        new_collaborator = {
            "collaborator_id": new_collaborator_id,
            "repository_id": new_repo_id,
            "user_id": new_owner_id,
            "permission_level": "admin",
            "status": "active",
            "added_at": timestamp,
        }

        # Add the new collaborator to the repository_collaborators dictionary
        repository_collaborators[new_collaborator_id] = new_collaborator

        return json.dumps({
            "success": True,
            "message": f"Repository '{source_repo.get('repository_name')}' forked successfully as '{new_repo_name}'",
            "repo_data": new_repo,
            "branches_count": len(new_branches),
            "directories_count": len(new_directories),
            "files_count": len(new_files),
            "file_contents_count": len(new_file_contents),
            "collaborator_data": new_collaborator,
            "parent_repo_id": source_repo_id
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return the tool specification for the fork_repo function."""
        return {
            "type": "function",
            "function": {
                "name": "fork_repo",
                "description": "Forks an existing repository into a new namespace in the version control system. Creates a copy of the source repository under a new owner with a new name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source_repo_id": {
                            "type": "string",
                            "description": "The ID of the source repository to fork.",
                        },
                        "new_owner_email": {
                            "type": "string",
                            "description": "The email address of the user who will own the forked repository.",
                        },
                        "new_repo_name": {
                            "type": "string",
                            "description": "The name of the new forked repository.",
                        },
                    },
                    "required": ["source_repo_id", "new_owner_email", "new_repo_name"],
                },
            },
        }
