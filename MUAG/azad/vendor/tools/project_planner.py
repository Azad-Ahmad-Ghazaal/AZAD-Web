from pathlib import Path
import json


class ProjectPlanner:

    def __init__(self, ai, project_memory):

        self.ai = ai
        self.project_memory = project_memory

    # =================================
    # BUILD PLANNING CONTEXT
    # =================================

    def _build_context(
        self,
        project_name,
        request
    ):

        project = self.project_memory.get_project(
            project_name
        )

        if not project:
            return None

        context = {
            "project": project_name,
            "request": request,
            "files": project.get(
                "files",
                []
            ),
            "dependencies": project.get(
                "dependencies",
                []
            ),
            "classes": project.get(
                "classes",
                []
            ),
            "functions": project.get(
                "functions",
                []
            ),
            "previous_fixes": project.get(
                "previous_fixes",
                []
            )
        }

        return context

    # =================================
    # BUILD AI PROMPT
    # =================================

    def _build_prompt(
        self,
        context
    ):

        return f"""
You are AZAD Project Planner.

Create a precise modification plan for an EXISTING Python project.

PROJECT:
{context["project"]}

USER REQUEST:
{context["request"]}

PROJECT FILES:
{json.dumps(context["files"], indent=2)}

DEPENDENCIES:
{json.dumps(context["dependencies"], indent=2)}

CLASSES:
{json.dumps(context["classes"], indent=2)}

FUNCTIONS:
{json.dumps(context["functions"], indent=2)}

PREVIOUS FIXES:
{json.dumps(context["previous_fixes"], indent=2)}

Determine:

1. Which existing file should be modified.
2. Which class or function is relevant.
3. Whether a new method/function is required.
4. Whether existing functionality must be preserved.
5. Whether tests should also be updated.
6. What exact change should be made.

IMPORTANT:

- Do not create a new project.
- Prefer existing implementation files.
- Do not modify tests unless the user explicitly requests test changes.
- Preserve existing functionality.
- Make the smallest change necessary.
- Do not invent files that do not exist.

Return ONLY valid JSON in this exact structure:

{{
    "filepath": "absolute filepath",
    "class": "class name or null",
    "method": "method name or null",
    "action": "modify or add",
    "modify_tests": false,
    "preserve_existing": true,
    "plan": "short precise description"
}}
"""

    # =================================
    # PLAN
    # =================================

    def plan(
        self,
        project_name,
        request
    ):

        context = self._build_context(
            project_name,
            request
        )

        if not context:

            return {
                "success": False,
                "message": "Project memory not found."
            }

        prompt = self._build_prompt(
            context
        )

        try:

            response = self.ai.ask(
                prompt
            )

        except Exception as e:

            return {
                "success": False,
                "message": (
                    "AI planning failed: "
                    + str(e)
                )
            }

        if not response:

            return {
                "success": False,
                "message": "AI returned an empty plan."
            }

        response = response.strip()

        # Remove markdown JSON fences
        if response.startswith(
            "```json"
        ):

            response = response[
                len("```json"):
            ]

        elif response.startswith(
            "```"
        ):

            response = response[
                len("```"):
            ]

        if response.endswith(
            "```"
        ):

            response = response[
                :-3
            ]

        response = response.strip()

        try:

            plan = json.loads(
                response
            )

        except json.JSONDecodeError as e:

            return {
                "success": False,
                "message": (
                    "AI returned invalid JSON: "
                    + str(e)
                ),
                "raw": response
            }

        required = [
            "filepath",
            "action",
            "modify_tests",
            "preserve_existing",
            "plan"
        ]

        for field in required:

            if field not in plan:

                return {
                    "success": False,
                    "message": (
                        "Plan missing field: "
                        + field
                    )
                }

        filepath = Path(
            plan["filepath"]
        )

        project_path = Path(
            project_name
        )

        # Validate against remembered files
        remembered_files = [
            str(
                Path(f).resolve()
            )
            for f in context["files"]
        ]

        try:

            resolved_filepath = (
                filepath.resolve()
            )

        except Exception:

            return {
                "success": False,
                "message": "Invalid filepath."
            }

        if str(
            resolved_filepath
        ) not in remembered_files:

            return {
                "success": False,
                "message": (
                    "Planner selected a file "
                    "that is not part of project memory."
                )
            }

        plan["filepath"] = str(
            resolved_filepath
        )

        plan["success"] = True

        return plan