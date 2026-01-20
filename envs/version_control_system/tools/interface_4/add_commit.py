import json
import os
import base64
import hashlib
import pathlib
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class AddCommit(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        auth_token: str,
        repository_id: str,
        branch_id: str,
        file_path: str,
        file_name: str,
        content: str,
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        # ------------------ TABLES ------------------
        access_tokens = data.get("access_tokens", {})
        repository_members = data.get("repository_collaborators", {})
        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        files = data.get("files", {})
        file_contents = data.get("file_contents", {})
        commits = data.get("commits", {})
        directories = data.get("directories", {})

        # ------------------ HELPERS ------------------
        def encode(text: str) -> str:
            return base64.b64encode(text.encode("utf-8")).decode("utf-8")

        def detect_language(file_identifier: str) -> str:
            if not file_identifier:
                return "Unknown"

            path = pathlib.Path(file_identifier)
            filename = path.name
            extension = path.suffix.lower()

            exact_matches = {
                "dockerfile": "Dockerfile",
                "makefile": "Makefile",
                "jenkinsfile": "Groovy",
            }

            if filename.lower() in exact_matches:
                return exact_matches[filename.lower()]

            extension_map = {
                ".c": "C",
                ".cpp": "C++",
                ".cc": "C++",
                ".cxx": "C++",
                ".hpp": "C++",
                ".cs": "C#",
                ".go": "Go",
                ".rs": "Rust",
                ".java": "Java",
                ".kt": "Kotlin",
                ".kts": "Kotlin",
                ".scala": "Scala",
                ".py": "Python",
                ".rb": "Ruby",
                ".php": "PHP",
                ".js": "JavaScript",
                ".mjs": "JavaScript",
                ".ts": "TypeScript",
                ".tsx": "TypeScript",
                ".sh": "Shell",
                ".ps1": "PowerShell",
                ".swift": "Swift",
                ".dart": "Dart",
                ".r": "R",
                ".groovy": "Groovy",
                ".pl": "Perl",
                ".pm": "Perl",
                ".lua": "Lua",
                ".hs": "Haskell",
                ".ex": "Elixir",
                ".exs": "Elixir",
                ".erl": "Erlang",
                ".hrl": "Erlang",
                ".jl": "Julia",
                ".s": "Assembly",
                ".asm": "Assembly",
                ".f": "Fortran",
                ".f90": "Fortran",
                ".cbl": "COBOL",
                ".cob": "COBOL",
                ".html": "HTML",
                ".htm": "HTML",
                ".css": "CSS",
                ".scss": "SCSS",
                ".less": "Less",
                ".md": "Markdown",
                ".json": "JSON",
                ".yaml": "YAML",
                ".yml": "YAML",
                ".xml": "XML",
                ".toml": "TOML",
                ".ini": "INI",
                ".csv": "CSV",
                ".tf": "Terraform",
                ".tfvars": "Terraform",
                ".sql": "SQL",
            }

            return extension_map.get(extension, "Unknown")

        # ------------------ AUTH ------------------
        encoded = encode(auth_token)
        token_info = next(
            (t for t in access_tokens.values() if t.get("token_encoded") == encoded),
            None,
        )

        if not token_info:
            return json.dumps(
                {"success": False, "error": "Invalid authentication token"}
            )

        requester_id = token_info.get("user_id")

        # ------------------ VALIDATION ------------------
        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required"})
        if not branch_id:
            return json.dumps({"success": False, "error": "branch_id is required"})
        if not file_name and not file_path:
            return json.dumps(
                {"success": False, "error": "file_name or file_path is required"}
            )
        if content is None:
            return json.dumps({"success": False, "error": "content is required"})

        repo = repositories.get(repository_id)
        if not repo:
            return json.dumps({"success": False, "error": "Repository not found"})

        # ------------------ PERMISSION CHECK ------------------
        membership = next(
            (
                m
                for m in repository_members.values()
                if m.get("repository_id") == repository_id
                and m.get("user_id") == requester_id
                and m.get("permission_level") in {"admin", "write"}
            ),
            None,
        )

        if not membership:
            return json.dumps(
                {
                    "success": False,
                    "error": "Permission denied. Admin or write access required.",
                }
            )

        # ------------------ BRANCH ------------------
        branch = branches.get(branch_id)
        if not branch or branch.get("repository_id") != repository_id:
            return json.dumps(
                {"success": False, "error": "Branch not found for repository"}
            )

        # ------------------ DIRECTORY RESOLUTION ------------------
        dir_path = os.path.dirname(file_path) if file_path else ""
        directory_id = None

        if dir_path:
            for d in directories.values():
                if (
                    d.get("directory_path") == dir_path
                    and d.get("repository_id") == repository_id
                    and d.get("branch_id") == branch_id
                ):
                    directory_id = d.get("directory_id")
                    break

        # ------------------ FILE LOOKUP ------------------
        existing_file = None
        for f in files.values():
            if (
                f.get("repository_id") == repository_id
                and f.get("branch_id") == branch_id
                and (
                    (file_path and f.get("file_path") == file_path)
                    or (file_name and f.get("file_name") == file_name)
                )
            ):
                existing_file = f
                break

        # ------------------ COMMIT ------------------
        try:
            next_commit_id = str(max(int(k) for k in commits.keys()) + 1)
        except ValueError:
            next_commit_id = "1"

        def generate_deterministic_sha(seed: str, prefix: str = "") -> str:
            return hashlib.sha1(f"{prefix}_{seed}".encode()).hexdigest()

        commit_sha = generate_deterministic_sha(next_commit_id, "azure")
        now = "2026-01-01T23:59:00"
        parent_commit_sha = branch.get("commit_sha")
        parent_commit_id = next(
            (
                commit["commit_id"]
                for commit in commits.values()
                if commit["commit_sha"] == parent_commit_sha
            ),
            None,
        )

        commit_entry = {
            "commit_id": str(next_commit_id),
            "repository_id": str(repository_id),
            "commit_sha": str(commit_sha),
            "author_id": str(requester_id),
            "committer_id": str(requester_id),
            "message": f"Add/update {file_path or file_name}",
            "parent_commit_id": str(parent_commit_id),
            "committed_at": now,
            "created_at": now,
        }

        commits[next_commit_id] = commit_entry
        branches[branch_id]["commit_sha"] = str(commit_sha)

        # ------------------ FILE ------------------
        try:
            next_file_id = str(max(int(k) for k in files.keys()) + 1)
        except ValueError:
            next_file_id = "1"

        file_identifier = file_path or file_name
        language = detect_language(file_identifier)

        if existing_file:
            file_id = existing_file["file_id"]
            files[file_id].update(
                {
                    "last_modified_at": now,
                    "last_commit_id": next_commit_id,
                    "updated_at": now,
                }
            )
        else:
            file_id = next_file_id
            files[file_id] = {
                "file_id": file_id,
                "repository_id": repository_id,
                "branch_id": branch_id,
                "directory_id": directory_id,
                "file_path": file_path or file_name,
                "file_name": file_name or os.path.basename(file_path or ""),
                "language": language,
                "is_binary": False,
                "last_modified_at": now,
                "last_commit_id": next_commit_id,
                "created_at": now,
                "updated_at": now,
            }

        # ------------------ CONTENT ------------------
        try:
            next_content_id = str(max(int(k) for k in file_contents.keys()) + 1)
        except ValueError:
            next_content_id = "1"

        file_contents[next_content_id] = {
            "content_id": next_content_id,
            "file_id": file_id,
            "commit_id": next_commit_id,
            "content": content,
            "encoding": "utf-8",
            "created_at": now,
        }

        return json.dumps(
            {
                "success": True,
                "commit": commit_entry,
                "file": files[file_id],
                "content": file_contents[next_content_id],
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_commit",
                "description": (
                    "Creates a new commit on a specified branch of a repository by adding or updating "
                    "a file. The requesting user must be authenticated and have either 'admin' or 'write' "
                    "permission on the target repository. "
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": (
                                "The unique identifier of the repository where the commit will be created. "
                            ),
                        },
                        "branch_id": {
                            "type": "string",
                            "description": (
                                "The unique identifier of the branch on which the commit will be applied. "
                                "The branch must belong to the specified repository."
                            ),
                        },
                        "file_path": {
                            "type": "string",
                            "description": (
                                "Optional full path of the file within the repository, including directories "
                                "(e.g., 'src/utils/helpers.py'). If provided, the directory structure is "
                                "used to locate or create the file."
                            ),
                        },
                        "file_name": {
                            "type": "string",
                            "description": (
                                "Optional name of the file to add or update. This may be provided instead of "
                                "file_path for files located at the repository root."
                            ),
                        },
                        "content": {
                            "type": "string",
                            "description": (
                                "The full textual content to be written to the file in this commit. "
                                "This value replaces any existing content for the file on the target branch."
                            ),
                        },
                        "auth_token": {
                            "type": "string",
                            "description": (
                                "Authentication token of the requesting user. The token is validated and "
                                "used to resolve the user identity and repository permissions."
                            ),
                        },
                    },
                    "required": [
                        "repository_id",
                        "branch_id",
                        "content",
                        "auth_token",
                        "file_path",
                        "file_name",
                    ],
                },
            },
        }
