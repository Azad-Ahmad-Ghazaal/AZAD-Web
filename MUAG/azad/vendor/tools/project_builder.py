import os
import json
import ast


class ProjectBuilder:

    def __init__(self, ai):
        self.ai = ai
        self.workspace = "workspace"

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

        # Remove markdown code fences.
        if response.startswith("```json"):

            response = response[len("```json"):]

        elif response.startswith("```python"):

            response = response[len("```python"):]

        elif response.startswith("```py"):

            response = response[len("```py"):]

        elif response.startswith("```"):

            response = response[3:]

        if response.endswith("```"):

            response = response[:-3]

        response = response.strip()

        return response

    def clean_python_code(self, code):

        if not code:
            return ""

        code = code.strip()

        # Remove markdown fences if the model ignored instructions.
        if code.startswith("```python"):

            code = code[len("```python"):]

        elif code.startswith("```py"):

            code = code[len("```py"):]

        elif code.startswith("```"):

            code = code[3:]

        if code.endswith("```"):

            code = code[:-3]

        lines = code.splitlines()

        cleaned_lines = []

        for index, line in enumerate(lines):

            stripped = line.strip()

            # Remove accidental language identifier.
            #
            # Example:
            #
            # python
            #
            # import unittest
            #
            # This should become:
            #
            # import unittest
            if (
                index == 0
                and stripped.lower() in (
                    "python",
                    "py",
                    "python3"
                )
            ):
                continue

            # Remove accidental markdown code fences.
            if stripped in (
                "```",
                "```python",
                "```py"
            ):
                continue

            cleaned_lines.append(line)

        code = "\n".join(
            cleaned_lines
        ).strip()

        return code

    def validate_python(
        self,
        code
    ):

        try:

            ast.parse(code)

            return {
                "valid": True,
                "error": ""
            }

        except SyntaxError as e:

            line_number = e.lineno or 0
            column = e.offset or 0

            message = e.msg or "Syntax error"

            return {
                "valid": False,
                "error": (
                    f"{message} "
                    f"(line {line_number}, column {column})"
                )
            }

        except Exception as e:

            return {
                "valid": False,
                "error": str(e)
            }

    def create_plan(
        self,
        request
    ):

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
8. Make sure every generated file can work together.
9. For Python projects, prefer a simple structure that can be tested easily.
10. Do not create unnecessary nested packages.
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

            if not isinstance(
                data["files"],
                list
            ):
                return None

            return data

        except Exception:

            return None

    def repair_python_file(
        self,
        request,
        project_name,
        file_path,
        purpose,
        code,
        error
    ):

        prompt = f"""
You are AZAD's Python code repair agent.

A Python file generated for a project contains a syntax error.

Project request:

{request}

Project name:

{project_name}

File:

{file_path}

Purpose:

{purpose}

CURRENT FILE:

---------------- FILE START ----------------

{code}

----------------- FILE END -----------------

Python validation error:

{error}

Your job is to return the COMPLETE corrected Python file.

IMPORTANT RULES:

1. Return ONLY the complete Python source code.
2. Do NOT use markdown.
3. Do NOT use ```python.
4. Do NOT add explanations.
5. Do NOT return partial code.
6. Preserve the intended functionality.
7. Fix indentation and syntax errors.
8. Use valid Python syntax.
9. Make sure imports are valid for the project structure.
10. Do not remove tests just to make the file pass.
11. If the file contains unittest tests, preserve all tests.
12. Do not write the word "python" as the first line.
"""

        try:

            response = self.ai.ask(
                prompt
            )

            repaired = self.clean_python_code(
                response
            )

            validation = self.validate_python(
                repaired
            )

            if validation["valid"]:

                return repaired

            return ""

        except Exception:

            return ""

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
5. Do NOT put the word "python" on the first line.
6. Write valid Python when the file is Python.
7. Make the file work with the other project files.
8. Use imports that match the generated project structure.
9. Do not invent unnecessary dependencies.
10. Use correct Python indentation.
11. If this is a test file, make it directly executable with Python.
12. If using unittest, include:

if __name__ == "__main__":
    unittest.main()

13. Return the complete file, including all imports, classes, functions and tests.
"""

        try:

            response = self.ai.ask(
                prompt
            )

            code = self.clean_python_code(
                response
            )

            # Only perform Python validation on .py files.
            if not file_path.lower().endswith(
                ".py"
            ):

                return code

            validation = self.validate_python(
                code
            )

            if validation["valid"]:

                return code

            # First generation contains invalid Python.
            # Ask the AI to repair the complete file.
            repaired = self.repair_python_file(
                request,
                project_name,
                file_path,
                purpose,
                code,
                validation["error"]
            )

            if repaired:

                return repaired

            return ""

        except Exception:

            return ""

    def safe_path(
        self,
        project_directory,
        relative_path
    ):

        relative_path = os.path.normpath(
            relative_path
        )

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

        # Prevent path traversal.
        try:

            common_path = os.path.commonpath(
                [
                    project_directory,
                    full_path
                ]
            )

        except ValueError:

            return None

        if common_path != project_directory:

            return None

        return full_path

    def build(
        self,
        request
    ):

        plan = self.create_plan(
            request
        )

        if not plan:

            return {
                "success": False,
                "message": "Could not create project plan.",
                "files": []
            }

        project_name = str(
            plan["project_name"]
        ).strip().replace(
            " ",
            "_"
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

                file.write(
                    code
                )

            created_files.append(
                full_path
            )

        return {
            "success": bool(created_files),
            "project": project_name,
            "directory": project_directory,
            "files": created_files,
            "plan": plan
        }