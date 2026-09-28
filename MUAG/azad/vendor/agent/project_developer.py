from pathlib import Path

from tools.project_memory import ProjectMemory
from tools.backup import BackupTool


class ProjectDeveloper:

    def __init__(self, ai, tester, auto_fixer=None):

        self.ai = ai
        self.tester = tester
        self.auto_fixer = auto_fixer

        self.memory = ProjectMemory()
        self.backup = BackupTool()

    # =================================
    # FIND PROJECT
    # =================================

    def find_project(self, project_name):

        project = self.memory.get_project(
            project_name
        )

        if project:
            return project

        return None

    # =================================
    # BUILD AI PROMPT
    # =================================

    def _build_prompt(
        self,
        project_name,
        request,
        project,
        filepath,
        code
    ):

        context = self.memory.get_context(
            project_name
        )

        prompt = f"""
You are AZAD Project Developer.

Modify an EXISTING project.

PROJECT:
{project_name}

USER REQUEST:
{request}

PROJECT MEMORY:
{context}

TARGET FILE:
{filepath}

CURRENT FILE CONTENT:

{code}

IMPORTANT RULES:

1. Modify the existing project.
2. Do not create a new project.
3. Preserve existing functionality.
4. Do not remove working features.
5. Implement only what the user requested.
6. Return the COMPLETE corrected file.
7. Do not use markdown code fences.
8. Do not explain before the code.
9. The response must contain valid Python code only.

Return the complete contents of:
{filepath}
"""

        return prompt

    # =================================
    # EXTRACT CODE
    # =================================

    def _clean_code(self, response):

        if not response:
            return ""

        code = response.strip()

        if code.startswith(
            "```python"
        ):

            code = code[
                len("```python"):
            ]

        elif code.startswith(
            "```"
        ):

            code = code[
                len("```"):
            ]

        if code.endswith(
            "```"
        ):

            code = code[
                :-3
            ]

        return code.strip()

    # =================================
    # SELECT FILE
    # =================================

    def _select_file(
        self,
        project,
        request
    ):

        files = project.get(
            "files",
            []
        )

        if not files:
            return None

        request_lower = request.lower()

        # Prefer main implementation file
        for filepath in files:

            path = Path(filepath)

            if (
                path.name.lower()
                in (
                    "main.py",
                    "app.py",
                    "program.py"
                )
            ):

                return filepath

        # Otherwise first Python source file
        for filepath in files:

            if (
                str(filepath).lower()
                .endswith(".py")
            ):

                filename = Path(
                    filepath
                ).name.lower()

                if not filename.startswith(
                    "test"
                ):

                    return filepath

        # Last fallback
        for filepath in files:

            if str(filepath).lower().endswith(
                ".py"
            ):

                return filepath

        return None

    # =================================
    # REFRESH PROJECT MEMORY
    # =================================

    def _refresh_memory(
        self,
        project_name,
        filepath,
        request,
        status
    ):

        """
        Keep project memory synchronized after
        a successful modification.

        The current ProjectMemory already stores
        project analysis and previous fixes.

        We update the fix history here without
        replacing the existing project structure.
        """

        try:

            self.memory.save_fix(
                project_name,
                filepath,
                request,
                status,
                1
            )

            return True

        except Exception:

            return False

    # =================================
    # DEVELOP PROJECT
    # =================================

    def develop(
        self,
        project_name,
        request
    ):

        result = {
            "success": False,
            "project": project_name,
            "filepath": None,
            "history": []
        }

        # ---------------------------------
        # FIND PROJECT
        # ---------------------------------

        project = self.find_project(
            project_name
        )

        if not project:

            result["message"] = (
                "Project memory not found."
            )

            return result

        # ---------------------------------
        # SELECT FILE
        # ---------------------------------

        filepath = self._select_file(
            project,
            request
        )

        if not filepath:

            result["message"] = (
                "No Python source file found."
            )

            return result

        path = Path(filepath)

        if not path.exists():

            result["message"] = (
                f"File not found: {filepath}"
            )

            return result

        result["filepath"] = str(
            path
        )

        # ---------------------------------
        # READ CURRENT FILE
        # ---------------------------------

        try:

            code = path.read_text(
                encoding="utf-8"
            )

        except Exception as e:

            result["message"] = (
                f"Could not read file: {e}"
            )

            return result

        result["history"].append(
            f"File selected: {filepath}"
        )

        # ---------------------------------
        # AI GENERATION
        # ---------------------------------

        prompt = self._build_prompt(
            project_name,
            request,
            project,
            filepath,
            code
        )

        result["history"].append(
            "Generating project modification..."
        )

        response = self.ai.ask(
            prompt
        )

        if not response:

            result["message"] = (
                "AI returned an empty response."
            )

            return result

        new_code = self._clean_code(
            response
        )

        if not new_code:

            result["message"] = (
                "AI did not generate valid code."
            )

            return result

        # ---------------------------------
        # BACKUP
        # ---------------------------------

        backup_result = self.backup.backup(
            filepath
        )

        result["history"].append(
            backup_result
        )

        # ---------------------------------
        # WRITE
        # ---------------------------------

        try:

            path.write_text(
                new_code,
                encoding="utf-8"
            )

        except Exception as e:

            result["message"] = (
                f"Could not write file: {e}"
            )

            return result

        result["history"].append(
            "Project modification applied."
        )

        # ---------------------------------
        # TEST
        # ---------------------------------

        result["history"].append(
            "Testing modified project..."
        )

        test_result = (
            self.tester.test_project(
                str(
                    path.parent
                )
            )
        )

        result["test_result"] = (
            test_result
        )

        # ---------------------------------
        # TEST SUCCESS
        # ---------------------------------

        if test_result["success"]:

            result["history"].append(
                "TEST STATUS: SUCCESS"
            )

            memory_updated = (
                self._refresh_memory(
                    project_name,
                    filepath,
                    request,
                    "Project modification completed successfully."
                )
            )

            if memory_updated:

                result["history"].append(
                    "PROJECT MEMORY UPDATED"
                )

            else:

                result["history"].append(
                    "PROJECT MEMORY UPDATE FAILED"
                )

            result["success"] = True

            return result

        # ---------------------------------
        # TEST FAILED
        # ---------------------------------

        result["history"].append(
            "TEST STATUS: FAILED"
        )

        # ---------------------------------
        # AUTO FIX
        # ---------------------------------

        if self.auto_fixer:

            result["history"].append(
                "Starting Auto-Fix..."
            )

            fix_result = (
                self.auto_fixer.fix_project(
                    str(
                        path.parent
                    ),
                    test_result
                )
            )

            result["fix_result"] = (
                fix_result
            )

            # ---------------------------------
            # AUTO FIX SUCCESS
            # ---------------------------------

            if fix_result["success"]:

                result["test_result"] = (
                    fix_result[
                        "test_result"
                    ]
                )

                result["history"].append(
                    "AUTO-FIX SUCCESS"
                )

                memory_updated = (
                    self._refresh_memory(
                        project_name,
                        filepath,
                        request,
                        "Project modification required Auto-Fix and was successfully repaired."
                    )
                )

                if memory_updated:

                    result["history"].append(
                        "PROJECT MEMORY UPDATED"
                    )

                else:

                    result["history"].append(
                        "PROJECT MEMORY UPDATE FAILED"
                    )

                result["success"] = True

                return result

            # ---------------------------------
            # AUTO FIX FAILED
            # ---------------------------------

            result["history"].append(
                "AUTO-FIX FAILED"
            )

        # ---------------------------------
        # FINAL FAILURE
        # ---------------------------------

        result["message"] = (
            "Project modification failed tests."
        )

        result["history"].append(
            "PROJECT MODIFICATION FAILED"
        )

        return result