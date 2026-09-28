import os

from tools.code_generator import CodeGenerator
from tools.write_file import WriteFileTool
from tools.read_file import ReadFileTool
from tools.python_runner import PythonRunner


class TaskExecutor:

    def __init__(self, ai):

        self.ai = ai

        self.generator = CodeGenerator(ai)

        self.writer = WriteFileTool()

        self.reader = ReadFileTool()

        self.runner = PythonRunner()

        self.workspace = "workspace"

        os.makedirs(
            self.workspace,
            exist_ok=True
        )

    # --------------------------------
    # Clean AI Code
    # --------------------------------

    def clean_code(self, code):

        if not code:
            return ""

        code = code.strip()

        # Remove markdown code fences

        if code.startswith("```python"):

            code = code[len("```python"):]

        elif code.startswith("```"):

            code = code[3:]

        if code.endswith("```"):

            code = code[:-3]

        return code.strip()

    # --------------------------------
    # Generate Code
    # --------------------------------

    def generate_code(self, request):

        try:

            code = self.generator.generate(
                request
            )

            return self.clean_code(code)

        except Exception as e:

            return ""

    # --------------------------------
    # Save Code
    # --------------------------------

    def save_code(
        self,
        filename,
        code
    ):

        filepath = os.path.join(
            self.workspace,
            filename
        )

        filepath = os.path.abspath(
            filepath
        )

        result = self.writer.write(
            filepath,
            code
        )

        return filepath, result

    # --------------------------------
    # Run Code
    # --------------------------------

    def run_code(self, filepath):

        try:

            return self.runner.run(
                filepath
            )

        except Exception as e:

            return f"Execution Failed\n\n{e}"

    # --------------------------------
    # Fix Existing Code
    # --------------------------------

    def fix_existing_file(
        self,
        filepath,
        max_attempts=3
    ):

        filepath = filepath.strip()

        if not os.path.exists(filepath):

            return {
                "success": False,
                "message": f"File not found: {filepath}",
                "history": []
            }

        history = []

        # Read existing code

        try:

            code = self.reader.read(
                filepath
            )

        except Exception as e:

            return {
                "success": False,
                "message": f"Could not read file: {e}",
                "history": history
            }

        for attempt in range(
            1,
            max_attempts + 1
        ):

            history.append(
                f"Attempt {attempt}: Testing existing code."
            )

            result = self.run_code(
                filepath
            )

            # Code works

            if "Execution Failed" not in result:

                history.append(
                    f"Attempt {attempt}: Code is working."
                )

                return {
                    "success": True,
                    "filepath": filepath,
                    "code": code,
                    "output": result,
                    "history": history
                }

            # Error found

            history.append(
                f"Attempt {attempt}: Error detected."
            )

            if attempt >= max_attempts:

                return {
                    "success": False,
                    "filepath": filepath,
                    "code": code,
                    "output": result,
                    "history": history
                }

            history.append(
                "AI is analyzing and fixing the code..."
            )

            fixed_code = self.ask_ai_to_fix(
                code,
                result
            )

            if not fixed_code:

                return {
                    "success": False,
                    "filepath": filepath,
                    "code": code,
                    "output": result,
                    "history": history
                }

            code = fixed_code

            # Save fixed code

            self.writer.write(
                filepath,
                code
            )

            history.append(
                f"Attempt {attempt}: Fixed code saved."
            )

        return {
            "success": False,
            "filepath": filepath,
            "code": code,
            "history": history
        }

    # --------------------------------
    # AI Fix
    # --------------------------------

    def ask_ai_to_fix(
        self,
        code,
        error
    ):

        prompt = f"""
You are AZAD's Python debugging engine.

A Python program failed during execution.

Your job is to FIX THE EXISTING PROGRAM.

IMPORTANT RULES:

1. Return ONLY complete Python source code.
2. Do NOT use markdown.
3. Do NOT use ```python.
4. Do NOT explain anything.
5. Do NOT return suggestions.
6. Do NOT return an example.
7. Keep the original purpose of the program.
8. Fix the EXACT error shown below.
9. Make sure every function body is correctly indented.
10. Make sure the final result is valid Python.
11. Do not leave any function empty.
12. Return the COMPLETE corrected file.

================ CURRENT CODE ================

{code}

================ ERROR ================

{error}

================ FINAL REQUIREMENT ================

Return ONLY the corrected Python code.
"""

        try:

            fixed = self.ai.ask(
                prompt
            )

            fixed = self.clean_code(
                fixed
            )

            if not fixed:
                return None

            # Basic validation before saving

            try:

                compile(
                    fixed,
                    "<azad_generated>",
                    "exec"
                )

            except SyntaxError:

                return None

            return fixed

        except Exception:

            return None

    # --------------------------------
    # Full Development Cycle
    # --------------------------------

    def execute(
        self,
        request,
        filename="generated.py",
        max_attempts=3
    ):

        history = []

        code = self.generate_code(
            request
        )

        if not code:

            return {
                "success": False,
                "message": "Code generation failed.",
                "history": history
            }

        # Check generated code before running

        try:

            compile(
                code,
                "<azad_generated>",
                "exec"
            )

        except SyntaxError as e:

            history.append(
                "Generated code contains a syntax error."
            )

            fixed = self.ask_ai_to_fix(
                code,
                str(e)
            )

            if fixed:

                code = fixed

                history.append(
                    "AI corrected the syntax error."
                )

            else:

                return {
                    "success": False,
                    "message": "AI could not generate valid Python code.",
                    "code": code,
                    "history": history
                }

        for attempt in range(
            1,
            max_attempts + 1
        ):

            filepath, save_result = self.save_code(
                filename,
                code
            )

            history.append(
                f"Attempt {attempt}: Code saved."
            )

            result = self.run_code(
                filepath
            )

            if "Execution Failed" not in result:

                history.append(
                    f"Attempt {attempt}: Execution successful."
                )

                return {
                    "success": True,
                    "filepath": filepath,
                    "code": code,
                    "output": result,
                    "history": history
                }

            history.append(
                f"Attempt {attempt}: Execution failed."
            )

            if attempt >= max_attempts:

                return {
                    "success": False,
                    "filepath": filepath,
                    "code": code,
                    "output": result,
                    "history": history
                }

            history.append(
                "AI is fixing the error..."
            )

            fixed_code = self.ask_ai_to_fix(
                code,
                result
            )

            if not fixed_code:

                history.append(
                    "AI could not produce valid corrected code."
                )

                return {
                    "success": False,
                    "filepath": filepath,
                    "code": code,
                    "output": result,
                    "history": history
                }

            code = fixed_code

            history.append(
                f"Attempt {attempt}: Code fixed."
            )

        return {
            "success": False,
            "message": "Maximum attempts reached.",
            "history": history
        }