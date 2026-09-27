from pathlib import Path
import ast
import json


class ProjectAnalyzer:

    def __init__(self, ai=None):
        self.ai = ai

    # =================================
    # FIND PYTHON FILES
    # =================================

    def _get_python_files(self, project_directory):

        project_path = Path(
            project_directory
        ).resolve()

        files = []

        if not project_path.exists():
            return files

        for filepath in project_path.rglob("*.py"):

            if "__pycache__" in filepath.parts:
                continue

            files.append(
                filepath
            )

        return sorted(files)

    # =================================
    # ANALYZE ONE FILE
    # =================================

    def _analyze_file(self, filepath):

        try:

            source = filepath.read_text(
                encoding="utf-8"
            )

            tree = ast.parse(
                source
            )

        except Exception as e:

            return {
                "file": str(filepath),
                "error": str(e),
                "imports": [],
                "classes": [],
                "functions": [],
            }

        imports = []
        classes = []
        functions = []

        for node in ast.walk(tree):

            # -------------------------
            # IMPORT
            # -------------------------

            if isinstance(
                node,
                ast.Import
            ):

                for item in node.names:

                    imports.append(
                        item.name
                    )

            elif isinstance(
                node,
                ast.ImportFrom
            ):

                module = (
                    node.module
                    or ""
                )

                imports.append(
                    module
                )

            # -------------------------
            # CLASS
            # -------------------------

            elif isinstance(
                node,
                ast.ClassDef
            ):

                methods = []

                for child in node.body:

                    if isinstance(
                        child,
                        (
                            ast.FunctionDef,
                            ast.AsyncFunctionDef
                        )
                    ):

                        methods.append(
                            child.name
                        )

                classes.append(
                    {
                        "name": node.name,
                        "methods": methods
                    }
                )

            # -------------------------
            # FUNCTION
            # -------------------------

            elif isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef
                )
            ):

                # Don't duplicate class methods
                parent_class = False

                for parent in ast.walk(tree):

                    if isinstance(
                        parent,
                        ast.ClassDef
                    ):

                        if node in parent.body:

                            parent_class = True
                            break

                if not parent_class:

                    functions.append(
                        node.name
                    )

        return {
            "file": str(filepath),
            "imports": sorted(
                set(imports)
            ),
            "classes": classes,
            "functions": sorted(
                set(functions)
            )
        }

    # =================================
    # IDENTIFY TEST FILES
    # =================================

    def _is_test_file(self, filepath):

        name = filepath.name.lower()

        return (
            name.startswith("test_")
            or name.startswith("test")
            or name.endswith("_test.py")
            or name == "tests.py"
        )

    # =================================
    # BUILD SUMMARY
    # =================================

    def _build_summary(
        self,
        project_name,
        file_analysis
    ):

        all_imports = set()
        all_classes = []
        all_functions = []

        test_files = []

        for item in file_analysis:

            filepath = Path(
                item["file"]
            )

            if self._is_test_file(
                filepath
            ):

                test_files.append(
                    str(filepath)
                )

            all_imports.update(
                item.get(
                    "imports",
                    []
                )
            )

            for class_info in item.get(
                "classes",
                []
            ):

                all_classes.append(
                    {
                        "file": str(filepath),
                        "name": class_info["name"],
                        "methods": class_info["methods"]
                    }
                )

            for function in item.get(
                "functions",
                []
            ):

                all_functions.append(
                    {
                        "file": str(filepath),
                        "name": function
                    }
                )

        return {
            "project": project_name,
            "files": [
                item["file"]
                for item in file_analysis
            ],
            "file_count": len(
                file_analysis
            ),
            "test_files": test_files,
            "test_count": len(
                test_files
            ),
            "dependencies": sorted(
                all_imports
            ),
            "classes": all_classes,
            "functions": all_functions
        }

    # =================================
    # AI PROJECT PURPOSE
    # =================================

    def _understand_project(
        self,
        summary
    ):

        if self.ai is None:

            return (
                "AI analysis unavailable."
            )

        prompt = f"""
Analyze this Python project.

Project:
{summary["project"]}

Files:
{json.dumps(summary["files"], indent=2)}

Dependencies:
{json.dumps(summary["dependencies"], indent=2)}

Classes:
{json.dumps(summary["classes"], indent=2)}

Functions:
{json.dumps(summary["functions"], indent=2)}

Tests:
{json.dumps(summary["test_files"], indent=2)}

Explain briefly:

1. What this project appears to do.
2. Its main components.
3. Important dependencies.
4. How the tests relate to the implementation.

Return a concise plain-text explanation.
"""

        try:

            result = self.ai.ask(
                prompt
            )

            if result:
                return result.strip()

        except Exception as e:

            return (
                "AI analysis failed: "
                + str(e)
            )

        return (
            "No project purpose analysis available."
        )

    # =================================
    # ANALYZE PROJECT
    # =================================

    def analyze(
        self,
        project_directory
    ):

        project_path = Path(
            project_directory
        ).resolve()

        project_name = (
            project_path.name
        )

        python_files = (
            self._get_python_files(
                project_directory
            )
        )

        file_analysis = []

        for filepath in python_files:

            file_analysis.append(
                self._analyze_file(
                    filepath
                )
            )

        summary = self._build_summary(
            project_name,
            file_analysis
        )

        summary["purpose"] = (
            self._understand_project(
                summary
            )
        )

        summary["file_analysis"] = (
            file_analysis
        )

        return summary