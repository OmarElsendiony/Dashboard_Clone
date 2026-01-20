import json
import hashlib
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreateFile(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        branch_id: str,
        file_path: str,
        file_name: str,
        language: str,
        is_binary: bool,
        content: str,
        encoding: str,
        commit_message: str,
        user_id: str,
    ) -> str:
        """Create a new file with file_content, commit and directory records."""
        timestamp = "2026-01-01T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            """Generate a new unique ID for a record."""
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        def generate_commit_sha(commit_id: str) -> str:
            """Generate commit SHA using hashlib."""
            return hashlib.sha1(f"commit_{commit_id}".encode()).hexdigest()

        # Validate data structure
        if not isinstance(data, dict):
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid data format: 'data' must be a dict",
                }
            )

        # Get data containers
        files_dict = data.get("files", {})
        file_contents_dict = data.get("file_contents", {})
        commits_dict = data.get("commits", {})
        branches_dict = data.get("branches", {})
        directories_dict = data.get("directories", {})
        repositories_dict = data.get("repositories", {})
        users_dict = data.get("users", {})

        # Convert to strings
        repository_id_str = str(repository_id).strip()
        branch_id_str = str(branch_id).strip()
        file_path_str = str(file_path).strip()
        file_name_str = str(file_name).strip()
        language_str = str(language).strip()
        is_binary_bool = bool(is_binary)
        content_str = str(content)
        encoding_str = str(encoding).strip()
        commit_message_str = str(commit_message).strip()
        user_id_str = str(user_id).strip()

        # Validate repository exists
        if repository_id_str not in repositories_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Repository with ID '{repository_id_str}' not found",
                }
            )

        # Validate branch exists
        if branch_id_str not in branches_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Branch with ID '{branch_id_str}' not found",
                }
            )

        # Validate branch belongs to repository
        branch = branches_dict[branch_id_str]
        if str(branch.get("repository_id")) != repository_id_str:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Branch '{branch_id_str}' does not belong to repository '{repository_id_str}'",
                }
            )

        # Validate user exists
        if user_id_str not in users_dict:
            return json.dumps(
                {
                    "success": False,
                    "error": f"User with ID '{user_id_str}' not found",
                }
            )

        # Validate encoding
        valid_encodings = ["utf-8", "base64", "binary"]
        if encoding_str not in valid_encodings:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid encoding '{encoding_str}'. Must be one of: {', '.join(valid_encodings)}",
                }
            )

        # Create directories for file_path
        directory_id = None
        new_dir = []
        if file_path_str:
            path_parts = file_path_str.split("/")
            current_path = ""
            parent_id = None

            for part in path_parts:
                if not part or part == file_name_str:
                    continue

                current_path = f"{current_path}/{part}" if current_path else part

                # Check if directory already exists
                existing_dir_id = None
                for dir_id, directory in directories_dict.items():
                    if (
                        isinstance(directory, dict)
                        and str(directory.get("repository_id")) == repository_id_str
                        and str(directory.get("directory_path")) == current_path
                    ):
                        existing_dir_id = str(dir_id)
                        break

                if existing_dir_id:
                    parent_id = existing_dir_id
                else:
                    # Create new directory
                    new_dir_id = generate_id(directories_dict)
                    new_directory = {
                        "directory_id": new_dir_id,
                        "repository_id": repository_id_str,
                        "directory_path": current_path,
                        "parent_directory_id": parent_id,
                        "created_at": timestamp,
                        "branch_id": branch_id_str,
                        "updated_at": timestamp,
                    }
                    new_dir.append(new_directory)
                    directories_dict[new_dir_id] = new_directory
                    parent_id = new_dir_id

            directory_id = parent_id


        for _, file in files_dict.items():
            if isinstance(file, dict) and str(file.get("repository_id")) == repository_id_str and str(file.get("file_name")) == file_name_str:
                # Check if directory_id matches (both could be None for root)
                if str(file.get("directory_id")) == str(directory_id):
                    return json.dumps({
                        "success": False,
                        "error": f"File with name '{file_name_str}' already exists in directory '{file_path_str or 'root'}'",
                    })

        # Create file first (to get file_id)
        new_file_id = generate_id(files_dict)

        # Create commit
        new_commit_id = generate_id(commits_dict)
        commit_sha = generate_commit_sha(new_commit_id)
        new_commit = {
            "commit_id": new_commit_id,
            "repository_id": repository_id_str,
            "commit_sha": commit_sha,
            "message": commit_message_str,
            "author_id": user_id_str,
            "committer_id": user_id_str,
            "committed_at": timestamp,
            "created_at": timestamp,
        }
        commits_dict[new_commit_id] = new_commit

        # Create file content with file_id and commit_id
        new_content_id = generate_id(file_contents_dict)
        new_file_content = {
            "content_id": new_content_id,
            "file_id": new_file_id,
            "commit_id": new_commit_id,
            "content": content_str,
            "encoding": encoding_str,
            "created_at": timestamp,
        }
        file_contents_dict[new_content_id] = new_file_content

        # Update branch with new commit_sha
        branches_dict[branch_id_str]["commit_sha"] = commit_sha

        # Validate language if provided
        if language is not None:
            valid_languages = [
                "C",
                "C++",
                "C#",
                "Go",
                "Rust",
                "Java",
                "Kotlin",
                "Scala",
                "Python",
                "Ruby",
                "PHP",
                "JavaScript",
                "TypeScript",
                "Shell",
                "PowerShell",
                "Swift",
                "Objective-C",
                "Dart",
                "R",
                "MATLAB",
                "Groovy",
                "Perl",
                "Lua",
                "Haskell",
                "Elixir",
                "Erlang",
                "Julia",
                "Assembly",
                "Fortran",
                "COBOL",
                "HTML",
                "CSS",
                "SCSS",
                "Less",
                "Markdown",
                "AsciiDoc",
                "JSON",
                "YAML",
                "XML",
                "TOML",
                "INI",
                "CSV",
                "Dockerfile",
                "Makefile",
                "Bash",
                "Terraform",
                "Ansible",
                "SQL",
                "PLpgSQL",
                "Text",
                "Binary",
                "Unknown",
            ]
            if language not in valid_languages:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid language '{language}'. Valid values: {', '.join(valid_languages)}",
                    }
                )
        # Create file record
        new_file = {
            "file_id": new_file_id,
            "repository_id": repository_id_str,
            "file_path": file_path_str,
            "file_name": file_name_str,
            "language": str(language_str),
            "is_binary": is_binary_bool,
            "encoding": str(encoding_str),
            "directory_id": directory_id,
            "created_at": timestamp,
            "updated_at": timestamp,
            "last_commit_id": new_commit_id,
            "branch_id": branch_id_str,
            "last_modified_at": timestamp,
        }
        files_dict[new_file_id] = new_file

        return json.dumps(
            {
                "success": True,
                "file": new_file,
                "file_content": new_file_content,
                "commit": new_commit,
                "directories": new_dir,
                "message": f"File '{file_name_str}' created successfully with commit {commit_sha[:7]}",
            }
        )

    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Return tool metadata for the create_file function."""
        return {
            "type": "function",
            "function": {
                "name": "create_file",
                "description": "Create a new file in a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the repository. Required",
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "The ID of the branch where the file is created. Required",
                        },
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file. Directories are auto-created. Required",
                        },
                        "file_name": {
                            "type": "string",
                            "description": "The name of the file. Required",
                        },
                        "language": {
                            "type": "string",
                            "description": "Required. The programming language of the file. Valid values: C, C++, C#, Go, Rust, Java, Kotlin, Scala, Python, Ruby, PHP, JavaScript, TypeScript, Shell, PowerShell, Swift, Objective-C, Dart, R, MATLAB, Groovy, Perl, Lua, Haskell, Elixir, Erlang, Julia, Assembly, Fortran, COBOL, HTML, CSS, SCSS, Less, Markdown, AsciiDoc, JSON, YAML, XML, TOML, INI, CSV, Dockerfile, Makefile, Bash, Terraform, Ansible, SQL, PLpgSQL, Text, Binary, Unknown. Optional",
                        },
                        "is_binary": {
                            "type": "boolean",
                            "description": "Required. Whether the file is binary.",
                        },
                        "content": {
                            "type": "string",
                            "description": "Required. The content of the file.",
                        },
                        "encoding": {
                            "type": "string",
                            "description": "Required. The encoding of the file Valid values: utf-8, base64, binary.",
                        },
                        "commit_message": {
                            "type": "string",
                            "description": "Required. The commit message for this file creation.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "Required. The ID of the user creating the file (used as author_id and committer_id).",
                        },
                    },
                    "required": [
                        "repository_id",
                        "branch_id",
                        "file_path",
                        "file_name",
                        "language",
                        "is_binary",
                        "content",
                        "encoding",
                        "commit_message",
                        "user_id",
                    ],
                },
            },
        }
