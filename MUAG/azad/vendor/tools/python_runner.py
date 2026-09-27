import subprocess
import sys


class PythonRunner:

    def run(self, filepath):

        try:

            result = subprocess.run(
                [sys.executable, filepath],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:

                return (
                    "Program Executed Successfully\n\n"
                    + result.stdout
                )

            return (
                "Execution Failed\n\n"
                + result.stderr
            )

        except Exception as e:

            return f"Error: {e}"