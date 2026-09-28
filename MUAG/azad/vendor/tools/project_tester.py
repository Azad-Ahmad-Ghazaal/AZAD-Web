import os
import subprocess
import sys


class ProjectTester:

    def __init__(self):
        pass

    # =================================
    # RUN NORMAL PYTHON FILE
    # =================================

    def run_file(
        self,
        filepath,
        cwd=None
    ):
        """
        Run a normal Python file directly.
        """

        try:

            result = subprocess.run(
                [
                    sys.executable,
                    filepath
                ],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )

            output = ""

            if result.stdout:
                output += result.stdout

            if result.stderr:

                if output:
                    output += "\n"

                output += result.stderr

            if result.returncode == 0:

                return {
                    "success": True,
                    "output": output.strip(),
                    "returncode": 0
                }

            return {
                "success": False,
                "output": output.strip(),
                "returncode": result.returncode
            }

        except subprocess.TimeoutExpired:

            return {
                "success": False,
                "output": "Program timed out.",
                "returncode": -1
            }

        except Exception as e:

            return {
                "success": False,
                "output": str(e),
                "returncode": -1
            }

    # =================================
    # RUN SINGLE TEST FILE
    # =================================

    def run_test_file(
        self,
        test_file,
        project_directory
    ):
        """
        Run one Python test file.
        """

        try:

            result = subprocess.run(
                [
                    sys.executable,
                    test_file
                ],
                cwd=project_directory,
                capture_output=True,
                text=True,
                timeout=30
            )

            output = ""

            if result.stdout:
                output += result.stdout

            if result.stderr:

                if output:
                    output += "\n"

                output += result.stderr

            if result.returncode == 0:

                return {
                    "success": True,
                    "output": output.strip(),
                    "returncode": 0
                }

            return {
                "success": False,
                "output": output.strip(),
                "returncode": result.returncode
            }

        except subprocess.TimeoutExpired:

            return {
                "success": False,
                "output": "Test timed out.",
                "returncode": -1
            }

        except Exception as e:

            return {
                "success": False,
                "output": str(e),
                "returncode": -1
            }

    # =================================
    # FIND ALL TEST FILES
    # =================================

    def find_test_files(
        self,
        project_directory
    ):
        """
        Find ALL test files in the project.

        Supports:
        test_*.py
        *_test.py
        tests/*.py
        """

        test_files = []

        for root, dirs, files in os.walk(
            project_directory
        ):

            # Ignore temporary AZAD folders
            dirs[:] = [
                d for d in dirs
                if not d.startswith(
                    "_azad_"
                )
            ]

            for filename in files:

                if not filename.endswith(
                    ".py"
                ):
                    continue

                if filename.startswith(
                    "test_"
                ):

                    test_files.append(
                        os.path.join(
                            root,
                            filename
                        )
                    )

                elif filename.endswith(
                    "_test.py"
                ):

                    test_files.append(
                        os.path.join(
                            root,
                            filename
                        )
                    )

        return sorted(
            test_files
        )

    # =================================
    # RUN COMPLETE TEST SUITE
    # =================================

    def run_test_suite(
        self,
        project_directory
    ):
        """
        Run the complete unittest test suite.

        This is the important part:
        AZAD now tests the PROJECT, not just
        one randomly selected test file.
        """

        try:

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-v"
                ],
                cwd=project_directory,
                capture_output=True,
                text=True,
                timeout=60
            )

            output = ""

            if result.stdout:
                output += result.stdout

            if result.stderr:

                if output:
                    output += "\n"

                output += result.stderr

            success = (
                result.returncode == 0
            )

            return {
                "success": success,
                "output": output.strip(),
                "returncode": result.returncode,
                "test_files": self.find_test_files(
                    project_directory
                )
            }

        except subprocess.TimeoutExpired:

            return {
                "success": False,
                "output": (
                    "Test suite timed out."
                ),
                "returncode": -1,
                "test_files": self.find_test_files(
                    project_directory
                )
            }

        except Exception as e:

            return {
                "success": False,
                "output": str(e),
                "returncode": -1,
                "test_files": self.find_test_files(
                    project_directory
                )
            }

    # =================================
    # FIND TEST FILE
    # =================================

    def find_test_file(
        self,
        project_directory
    ):
        """
        Backward-compatible method.

        Returns the first test file.
        """

        test_files = self.find_test_files(
            project_directory
        )

        if test_files:

            return test_files[0]

        return None

    # =================================
    # TEST PROJECT
    # =================================

    def test_project(
        self,
        project_directory
    ):
        """
        Main project testing entry point.

        Priority:

        1. Full unittest suite
        2. Main.py execution
        """

        test_files = self.find_test_files(
            project_directory
        )

        # ---------------------------------
        # TEST SUITE
        # ---------------------------------

        if test_files:

            return self.run_test_suite(
                project_directory
            )

        # ---------------------------------
        # MAIN.PY FALLBACK
        # ---------------------------------

        main_file = os.path.join(
            project_directory,
            "main.py"
        )

        if os.path.exists(
            main_file
        ):

            return self.run_file(
                main_file,
                cwd=project_directory
            )

        return {
            "success": False,
            "output": (
                "No test files or main.py "
                "found."
            ),
            "returncode": -1,
            "test_files": []
        }