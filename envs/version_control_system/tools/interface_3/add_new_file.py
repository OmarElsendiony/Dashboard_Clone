import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class AddNewFile(Tool):

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        branch_id: str,
        file_path: str,
        file_name: str,
        directory_id: Optional[str] = None,
        language: Optional[str] = None,
        is_binary: Optional[bool] = False
    ) -> str:
        """
        Creates a new file in a repository.
        """
        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid payload: data must be dict."})

        if not repository_id:
            return json.dumps({"success": False, "error": "repository_id is required to add new file"})
        if not branch_id:
            return json.dumps({"success": False, "error": "branch_id is required to add new file"})
        if not file_path:
            return json.dumps({"success": False, "error": "file_path is required to add new file"})
        if not file_name:
            return json.dumps({"success": False, "error": "file_name is required to add new file"})

        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        directories = data.get("directories", {})
        files = data.get("files", {})

        # Validate repository exists
        if str(repository_id) not in repositories:
            return json.dumps({"success": False, "error": f"Repository with id '{repository_id}' not found"})

        # Validate branch exists
        if str(branch_id) not in branches:
            return json.dumps({"success": False, "error": f"Branch with id '{branch_id}' not found"})

        # Validate branch belongs to the repository
        branch = branches[str(branch_id)]
        if str(branch.get("repository_id")) != str(repository_id):
            return json.dumps({"success": False, "error": f"Branch '{branch_id}' does not belong to repository '{repository_id}'"})

        # Validate directory_id exists if provided
        if directory_id is not None:
            if str(directory_id) not in directories:
                return json.dumps({"success": False, "error": f"Directory with id '{directory_id}' not found"})

        # Validate language if provided
        if language is not None:
            valid_languages = [
                "C", "C++", "C#", "Go", "Rust", "Java", "Kotlin", "Scala", "Python", "Ruby",
                "PHP", "JavaScript", "TypeScript", "Shell", "PowerShell", "Swift", "Objective-C",
                "Dart", "R", "MATLAB", "Groovy", "Perl", "Lua", "Haskell", "Elixir", "Erlang",
                "Julia", "Assembly", "Fortran", "COBOL", "HTML", "CSS", "SCSS", "Less", "Markdown",
                "AsciiDoc", "JSON", "YAML", "XML", "TOML", "INI", "CSV", "Dockerfile", "Makefile",
                "Bash", "Terraform", "Ansible", "SQL", "PLpgSQL", "Text", "Binary", "Unknown"
            ]
            if language not in valid_languages:
                return json.dumps({"success": False, "error": f"Invalid language '{language}'. Valid values: {', '.join(valid_languages)}"})

        # Check if file already exists at the same path in this repository and branch
        for file_id, file in files.items():
            if (str(file.get("repository_id")) == str(repository_id) and
                str(file.get("branch_id")) == str(branch_id) and
                file.get("file_path") == file_path and
                file.get("file_name") == file_name):
                return json.dumps({"success": False, "error": f"File '{file_name}' already exists at path '{file_path}' in this branch"})

        # Generate new file_id
        if files:
            max_file_id = max(int(k) for k in files.keys())
            new_file_id = str(max_file_id + 1)
        else:
            new_file_id = "1"

        # Create file record
        new_file = {
            "file_id": new_file_id,
            "repository_id": repository_id,
            "branch_id": branch_id,
            "directory_id": directory_id,
            "file_path": file_path,
            "file_name": file_name,
            "is_binary": is_binary,
            "language": language,
            "created_at": "2026-01-01T23:59:00"
        }

        files[new_file_id] = new_file

        return json.dumps({"success": True, "result": new_file})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_new_file",
                "description": "Creates a new file in a repository branch. The file path and name combination must be unique within the branch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The unique identifier of the repository to add the file to."
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "The unique identifier of the branch to add the file to."
                        },
                        "file_path": {
                            "type": "string",
                            "description": "The directory path where the file will be created (e.g., 'src/utils')."
                        },
                        "file_name": {
                            "type": "string",
                            "description": "The name of the file including extension (e.g., 'helper.py')."
                        },
                        "directory_id": {
                            "type": "string",
                            "description": "The unique identifier of the directory the file belongs to. Optional."
                        },
                        "language": {
                            "type": "string",
                            "description": "The programming language of the file. Valid values: C, C++, C#, Go, Rust, Java, Kotlin, Scala, Python, Ruby, PHP, JavaScript, TypeScript, Shell, PowerShell, Swift, Objective-C, Dart, R, MATLAB, Groovy, Perl, Lua, Haskell, Elixir, Erlang, Julia, Assembly, Fortran, COBOL, HTML, CSS, SCSS, Less, Markdown, AsciiDoc, JSON, YAML, XML, TOML, INI, CSV, Dockerfile, Makefile, Bash, Terraform, Ansible, SQL, PLpgSQL, Text, Binary, Unknown. Optional."
                        },
                        "is_binary": {
                            "type": "boolean",
                            "description": "Whether the file is a binary file. Default: false."
                        }
                    },
                    "required": ["repository_id", "branch_id", "file_path", "file_name"]
                }
            }
        }
