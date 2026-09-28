import os
import json


class ProjectBuilder:

    def __init__(self, ai):

        self.ai = ai

        self.workspace = "workspace"

    # =================================
    # CLEAN AI RESPONSE
    # =================================

    def clean_response(self, response):

        if response is None:
            return ""

        if not isinstance(response, str):

            try:
                response = json.dumps(
                    response,
                    ensure_ascii=False
                )
            except Exception:
                response = str(response)

        response = response.strip()

        if response.startswith("```json"):

            response = response[
                len("```json"):
            ]

        elif response.startswith("```"):

            response = response[3:]

        if response.endswith("```"):

            response = response[:-3]

        return response.strip()

    # =================================
    # CREATE PROJECT PLAN
    # =================================

    def create_plan(self, request):

        prompt = f"""
You are AZAD's Project Architect.

Create a project structure for this request:

{request}

Return ONLY valid JSON.

Format:

{{
    "project_name": "project_name",
    "files": [
        {{
            "path": "main.py",
            "purpose": "main application"
        }}
    ]
}}

Rules:

1. Return ONLY JSON.
2. No markdown.
3. No explanations.
4. Use relative paths only.
5. Do not include D:\\Azad.
6. Keep the project reasonably small.
7. Include tests when appropriate.
"""

        try:

            response = self.ai.ask(
                prompt
            )

            response = self.clean_response(
                response
            )

            data = json.loads(
                response
            )

            if not isinstance(
                data,
                dict
            ):

                return None

            if "project_name" not in data:

                return None

            if "files" not in data:

                return None

            return data

        except Exception:

            return None

    # =================================
    # GENERATE FILE
    # =================================

    def generate_file(
        self,
        request,
        project_name,
        file_path,
        purpose
    ):

        prompt = f"""
You are AZAD's Python developer.

Build this project:

{request}

Project name:

{project_name}

Create this file:

{file_path}

Purpose:

{purpose}

Rules:

1. Return ONLY the complete file content.
2. Do NOT use markdown.
3. Do NOT use ```python.
4. Do NOT explain anything.
5. Write valid Python when the file is Python.
6. Make the file work with the other project files.
7. Use relative imports when necessary.
8. Do not invent unnecessary dependencies.
"""

        try:

            response = self.ai.ask(
                prompt
            )

            response = self.clean_response(
                response
            )

            return response

        except Exception:

            return ""

    # =================================
    # SAFE PATH
    # =================================

    def safe_path(
        self,
        project_directory,
        relative_path
    ):

        relative_path = os.path.normpath(
            relative_path
        )

        # Prevent paths escaping project

        if (
            relative_path.startswith("..")
            or os.path.isabs(relative_path)
        ):

            return None

        full_path = os.path.abspath(
            os.path.join(
                project_directory,
                relative_path
            )
        )

        project_directory = os.path.abspath(
            project_directory
        )

        if not full_path.startswith(
            project_directory
        ):

            return None

        return full_path

    # =================================
    # BUILD PROJECT
    # =================================

    def build(self, request):

        plan = self.create_plan(
            request
        )

        if not plan:

            return {
                "success": False,
                "message": "Could not create project plan.",
                "files": []
            }

        project_name = plan[
            "project_name"
        ]

        # Clean project name

        project_name = (
            str(project_name)
            .strip()
            .replace(" ", "_")
        )

        project_directory = os.path.abspath(
            os.path.join(
                self.workspace,
                project_name
            )
        )

        os.makedirs(
            project_directory,
            exist_ok=True
        )

        created_files = []

        for file_info in plan["files"]:

            if not isinstance(
                file_info,
                dict
            ):

                continue

            path = file_info.get(
                "path",
                ""
            )

            purpose = file_info.get(
                "purpose",
                ""
            )

            if not path:

                continue

            full_path = self.safe_path(
                project_directory,
                path
            )

            if full_path is None:

                continue

            code = self.generate_file(
                request,
                project_name,
                path,
                purpose
            )

            if not code:

                continue

            folder = os.path.dirname(
                full_path
            )

            os.makedirs(
                folder,
                exist_ok=True
            )

            with open(
                full_path,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(code)

            created_files.append(
                full_path
            )

        return {
            "success": bool(
                created_files
            ),
            "project": project_name,
            "directory": project_directory,
            "files": created_files,
            "plan": plan
        }