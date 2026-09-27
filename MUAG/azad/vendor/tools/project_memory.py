from datetime import datetime
from core.memory import Memory


class ProjectMemory:

    def __init__(self):
        self.memory = Memory()

    # =================================
    # PROJECT KEY
    # =================================

    def _key(self, project_name):

        return (
            "project:"
            + project_name
        )

    # =================================
    # SAVE PROJECT
    # =================================

    def save_project(
        self,
        project_name,
        analysis
    ):

        existing = self.get_project(
            project_name
        )

        if not isinstance(
            existing,
            dict
        ):
            existing = {}

        project_data = dict(
            analysis
        )

        # Preserve previous fixes
        previous_fixes = existing.get(
            "previous_fixes",
            []
        )

        project_data[
            "previous_fixes"
        ] = previous_fixes

        project_data[
            "last_analyzed"
        ] = datetime.now().isoformat(
            timespec="seconds"
        )

        self.memory.save(
            self._key(project_name),
            project_data
        )

        return project_data

    # =================================
    # GET PROJECT
    # =================================

    def get_project(
        self,
        project_name
    ):

        result = self.memory.remember(
            self._key(project_name)
        )

        if isinstance(
            result,
            dict
        ):

            return result

        return None

    # =================================
    # PROJECT EXISTS
    # =================================

    def exists(
        self,
        project_name
    ):

        return (
            self.get_project(
                project_name
            )
            is not None
        )

    # =================================
    # SAVE FIX
    # =================================

    def save_fix(
        self,
        project_name,
        filepath,
        reason,
        explanation="",
        attempt=1
    ):

        project = self.get_project(
            project_name
        )

        if project is None:

            project = {
                "project": project_name,
                "previous_fixes": []
            }

        fixes = project.get(
            "previous_fixes",
            []
        )

        fixes.append(
            {
                "filepath": str(filepath),
                "reason": str(reason),
                "explanation": str(
                    explanation
                ),
                "attempt": attempt,
                "timestamp": datetime.now().isoformat(
                    timespec="seconds"
                )
            }
        )

        project[
            "previous_fixes"
        ] = fixes

        project[
            "last_updated"
        ] = datetime.now().isoformat(
            timespec="seconds"
        )

        self.memory.save(
            self._key(project_name),
            project
        )

        return project

    # =================================
    # GET FILES
    # =================================

    def get_files(
        self,
        project_name
    ):

        project = self.get_project(
            project_name
        )

        if not project:
            return []

        return project.get(
            "files",
            []
        )

    # =================================
    # GET DEPENDENCIES
    # =================================

    def get_dependencies(
        self,
        project_name
    ):

        project = self.get_project(
            project_name
        )

        if not project:
            return []

        return project.get(
            "dependencies",
            []
        )

    # =================================
    # GET CLASSES
    # =================================

    def get_classes(
        self,
        project_name
    ):

        project = self.get_project(
            project_name
        )

        if not project:
            return []

        return project.get(
            "classes",
            []
        )

    # =================================
    # GET FUNCTIONS
    # =================================

    def get_functions(
        self,
        project_name
    ):

        project = self.get_project(
            project_name
        )

        if not project:
            return []

        return project.get(
            "functions",
            []
        )

    # =================================
    # GET FIX HISTORY
    # =================================

    def get_fix_history(
        self,
        project_name
    ):

        project = self.get_project(
            project_name
        )

        if not project:
            return []

        return project.get(
            "previous_fixes",
            []
        )

    # =================================
    # BUILD DEVELOPMENT CONTEXT
    # =================================

    def get_context(
        self,
        project_name
    ):

        project = self.get_project(
            project_name
        )

        if not project:

            return (
                "No project memory found."
            )

        lines = []

        lines.append(
            "PROJECT MEMORY"
        )

        lines.append(
            f"Project: {project.get('project', project_name)}"
        )

        lines.append("")

        lines.append(
            "Purpose:"
        )

        lines.append(
            str(
                project.get(
                    "purpose",
                    "Unknown"
                )
            )
        )

        lines.append("")

        lines.append(
            "Files:"
        )

        for filepath in project.get(
            "files",
            []
        ):

            lines.append(
                f"- {filepath}"
            )

        lines.append("")

        lines.append(
            "Dependencies:"
        )

        for dependency in project.get(
            "dependencies",
            []
        ):

            lines.append(
                f"- {dependency}"
            )

        lines.append("")

        lines.append(
            "Classes:"
        )

        for class_info in project.get(
            "classes",
            []
        ):

            lines.append(
                f"- {class_info.get('name')}"
            )

            for method in class_info.get(
                "methods",
                []
            ):

                lines.append(
                    f"  - {method}"
                )

        lines.append("")

        lines.append(
            "Previous Fixes:"
        )

        fixes = project.get(
            "previous_fixes",
            []
        )

        if not fixes:

            lines.append(
                "- None"
            )

        else:

            for fix in fixes:

                lines.append(
                    f"- {fix.get('filepath')}: "
                    f"{fix.get('reason')}"
                )

        return "\n".join(
            lines
        )