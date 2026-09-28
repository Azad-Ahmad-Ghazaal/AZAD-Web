import os
import shutil
import time


class AutoFixer:

    def __init__(self, ai, project_tester):
        self.ai = ai
        self.project_tester = project_tester
        self.max_attempts = 3

    def fix_project(
        self,
        project_directory,
        initial_test_result
    ):
        """
        Automatically fix project test errors.

        The AI analyzes the test error, identifies the responsible
        Python file, generates a complete replacement, saves a backup,
        applies the fix, and runs the project tests again.
        """

        history = []

        current_test_result = initial_test_result

        attempts = 0

        while (
            attempts < self.max_attempts
            and not current_test_result["success"]
        ):
            attempts += 1

            history.append(
                f"Attempt {attempts}: "
                "Testing existing code."
            )

            error_output = current_test_result.get(
                "output",
                "Unknown error."
            )

            # ---------------------------------
            # COLLECT PROJECT PYTHON FILES
            # ---------------------------------

            files_list = []

            for root, dirs, files in os.walk(
                project_directory
            ):
                dirs[:] = [
                    directory
                    for directory in dirs
                    if directory != "_azad_test_package"
                ]

                for filename in files:

                    if not filename.endswith(".py"):
                        continue

                    full_path = os.path.join(
                        root,
                        filename
                    )

                    relative_path = os.path.relpath(
                        full_path,
                        project_directory
                    )

                    files_list.append(
                        relative_path
                    )

            # ---------------------------------
            # BUILD AI DEBUGGING PROMPT
            # ---------------------------------

            prompt = (
                "You are an expert Python developer and "
                "debugging assistant.\n\n"

                "A Python project has failed its test.\n\n"

                "TEST ERROR:\n"
                f"{error_output}\n\n"

                "AVAILABLE PYTHON FILES:\n"
                f"{', '.join(files_list)}\n\n"

                "Your task is to identify the file responsible "
                "for the error and provide the complete corrected "
                "code for that file.\n\n"

                "IMPORTANT RULES:\n"
                "1. Select exactly one file from the available files.\n"
                "2. Do not invent a filename.\n"
                "3. Return the COMPLETE contents of the corrected file.\n"
                "4. Do not return partial code.\n"
                "5. Do not include explanations inside the CODE section.\n\n"

                "Use exactly this format:\n\n"

                "FILE: relative/path/to/file.py\n"
                "REASON: short explanation\n"
                "CODE:\n"
                "```python\n"
                "complete corrected code\n"
                "```\n"
            )

            # ---------------------------------
            # ASK AI
            # ---------------------------------

            try:

                ai_response = self.ai.generate(
                    prompt
                )

            except Exception as e:

                history.append(
                    f"Attempt {attempts}: "
                    f"AI error: {str(e)}"
                )

                continue

            if not ai_response:

                history.append(
                    f"Attempt {attempts}: "
                    "AI returned an empty response."
                )

                continue

            # ---------------------------------
            # PARSE AI RESPONSE
            # ---------------------------------

            target_file, fixed_code = (
                self._parse_ai_fix_response(
                    ai_response,
                    files_list
                )
            )

            if not target_file:

                history.append(
                    f"Attempt {attempts}: "
                    "AI did not identify a valid target file."
                )

                continue

            if not fixed_code:

                history.append(
                    f"Attempt {attempts}: "
                    "AI did not provide corrected code."
                )

                continue

            # ---------------------------------
            # VALIDATE TARGET PATH
            # ---------------------------------

            normalized_target = os.path.normpath(
                target_file
            )

            if (
                normalized_target.startswith("..")
                or os.path.isabs(normalized_target)
            ):

                history.append(
                    f"Attempt {attempts}: "
                    "AI returned an invalid file path."
                )

                continue

            full_file_path = os.path.join(
                project_directory,
                normalized_target
            )

            if not os.path.exists(
                full_file_path
            ):

                history.append(
                    f"Attempt {attempts}: "
                    f"Target file does not exist: "
                    f"{target_file}"
                )

                continue

            # ---------------------------------
            # CREATE BACKUP
            # ---------------------------------

            backup_dir = os.path.join(
                "backups",
                "auto_fixer",
                time.strftime(
                    "%Y%m%d_%H%M%S"
                )
            )

            os.makedirs(
                backup_dir,
                exist_ok=True
            )

            backup_filename = (
                os.path.basename(
                    normalized_target
                )
            )

            backup_path = os.path.join(
                backup_dir,
                backup_filename
            )

            try:

                shutil.copy2(
                    full_file_path,
                    backup_path
                )

                history.append(
                    f"Backup created: {backup_path}"
                )

            except Exception as e:

                history.append(
                    f"Warning: backup failed: {str(e)}"
                )

            # ---------------------------------
            # SAVE FIXED CODE
            # ---------------------------------

            try:

                with open(
                    full_file_path,
                    "w",
                    encoding="utf-8"
                ) as file:

                    file.write(
                        fixed_code
                    )

                history.append(
                    f"Attempt {attempts}: "
                    f"Fixed code saved to {target_file}."
                )

            except Exception as e:

                history.append(
                    f"Attempt {attempts}: "
                    f"Failed to save fix: {str(e)}"
                )

                continue

            # ---------------------------------
            # TEST AGAIN
            # ---------------------------------

            history.append(
                f"Attempt {attempts}: "
                "Testing fixed code."
            )

            current_test_result = (
                self.project_tester.test_project(
                    project_directory
                )
            )

            if current_test_result["success"]:

                history.append(
                    f"Attempt {attempts}: "
                    "Code is working."
                )

                return {
                    "success": True,
                    "attempts": attempts,
                    "history": history,
                    "test_result": current_test_result
                }

            history.append(
                f"Attempt {attempts}: "
                "Error still exists."
            )

        # ---------------------------------
        # FINAL FAILURE
        # ---------------------------------

        return {
            "success": False,
            "attempts": attempts,
            "history": history,
            "test_result": current_test_result
        }

    def _parse_ai_fix_response(
        self,
        response_text,
        files_list
    ):
        """
        Extract target file and complete corrected code
        from the AI response.
        """

        target_file = None

        fixed_code = None

        lines = response_text.splitlines()

        capturing_code = False

        code_lines = []

        # ---------------------------------
        # FIND FILE
        # ---------------------------------

        for line in lines:

            stripped = line.strip()

            if stripped.upper().startswith(
                "FILE:"
            ):

                potential_file = (
                    stripped[
                        len("FILE:"):
                    ].strip()
                )

                potential_file = (
                    potential_file
                    .strip(
                        "`'\" "
                    )
                )

                potential_file = os.path.normpath(
                    potential_file
                )

                for available_file in files_list:

                    if os.path.normpath(
                        available_file
                    ) == potential_file:

                        target_file = (
                            available_file
                        )

                        break

            # ---------------------------------
            # START CODE BLOCK
            # ---------------------------------

            elif (
                stripped.lower() == "```python"
                or stripped.lower() == "```py"
                or stripped.lower().startswith(
                    "```python"
                )
            ):

                capturing_code = True

                continue

            # ---------------------------------
            # END CODE BLOCK
            # ---------------------------------

            elif (
                capturing_code
                and stripped == "```"
            ):

                capturing_code = False

                continue

            # ---------------------------------
            # COLLECT CODE
            # ---------------------------------

            elif capturing_code:

                code_lines.append(
                    line
                )

        # ---------------------------------
        # FALLBACK FILE DETECTION
        # ---------------------------------

        if not target_file:

            normalized_response = (
                response_text.replace(
                    "\\",
                    "/"
                )
            )

            for available_file in files_list:

                normalized_file = (
                    available_file.replace(
                        "\\",
                        "/"
                    )
                )

                if normalized_file in normalized_response:

                    target_file = (
                        available_file
                    )

                    break

        # ---------------------------------
        # FALLBACK CODE EXTRACTION
        # ---------------------------------

        if code_lines:

            fixed_code = "\n".join(
                code_lines
            ).strip()

        else:

            # Try extracting anything between
            # generic triple backticks.

            start_marker = response_text.find(
                "```"
            )

            if start_marker >= 0:

                first_newline = (
                    response_text.find(
                        "\n",
                        start_marker
                    )
                )

                if first_newline >= 0:

                    end_marker = (
                        response_text.find(
                            "```",
                            first_newline + 1
                        )
                    )

                    if end_marker >= 0:

                        fixed_code = (
                            response_text[
                                first_newline + 1:
                                end_marker
                            ].strip()
                        )

        # ---------------------------------
        # REMOVE ACCIDENTAL MARKDOWN FENCES
        # ---------------------------------

        if fixed_code:

            fixed_code = fixed_code.strip()

            if fixed_code.startswith(
                "```"
            ):

                first_newline = (
                    fixed_code.find(
                        "\n"
                    )
                )

                if first_newline >= 0:

                    fixed_code = (
                        fixed_code[
                            first_newline + 1:
                        ]
                    )

            if fixed_code.endswith(
                "```"
            ):

                fixed_code = (
                    fixed_code[
                        :-3
                    ]
                    .rstrip()
                )

        return (
            target_file,
            fixed_code
        )