from core.developer import Developer
from core.task_executor import TaskExecutor

from tools.project_builder import ProjectBuilder
from tools.project_tester import ProjectTester
from tools.auto_fixer import AutoFixer
from tools.project_analyzer import ProjectAnalyzer
from tools.project_developer import ProjectDeveloper
from tools.self_improver import SelfImprover

from core.memory import Memory


class DeveloperAgent:

    def __init__(self, ai):

        self.ai = ai

        self.developer = Developer(
            ai
        )

        self.executor = TaskExecutor(
            ai
        )

        self.project_builder = ProjectBuilder(
            ai
        )

        self.project_tester = ProjectTester()

        self.auto_fixer = AutoFixer(
            ai,
            self.project_tester
        )

        self.project_analyzer = ProjectAnalyzer(
            ai
        )

        self.memory = Memory()

        # =================================
        # PROJECT DEVELOPER
        # =================================

        self.project_developer = ProjectDeveloper(
            ai,
            self.project_tester,
            self.auto_fixer
        )

        # =================================
        # SELF IMPROVER
        # =================================

        self.self_improver = SelfImprover(
            ai,
            self.project_tester,
            self.project_analyzer,
            self.memory
        )

    # =================================
    # NORMAL DEVELOP
    # =================================

    def handle_develop(
        self,
        message
    ):

        request = message[
            8:
        ].strip()

        if not request:

            return (
                "Please describe what "
                "you want me to develop."
            )

        words = request.split()

        existing_project = None

        if words:

            possible_project = words[0]

            if self.project_developer.find_project(
                possible_project
            ):

                existing_project = (
                    possible_project
                )

        # =================================
        # EXISTING PROJECT
        # =================================

        if existing_project:

            project_request = (
                " ".join(
                    words[1:]
                ).strip()
            )

            if not project_request:
                project_request = request

            result = (
                self.project_developer.develop(
                    existing_project,
                    project_request
                )
            )

            output = []

            output.append(
                "========== AZAD PROJECT DEVELOPER =========="
            )

            output.append("")
            output.append(
                f"Project: {existing_project}"
            )
            output.append("")

            if result["success"]:

                output.append(
                    "STATUS: PROJECT UPDATED"
                )

                output.append("")

                output.append(
                    f"File: {result.get('filepath', 'Unknown')}"
                )

                output.append("")

                output.append(
                    "========== DEVELOPMENT =========="
                )

                output.append("")

                for item in result.get(
                    "history",
                    []
                ):

                    output.append(
                        str(item)
                    )

                output.append("")

                test_result = result.get(
                    "test_result"
                )

                if test_result:

                    output.append(
                        "========== FINAL TEST =========="
                    )

                    output.append("")

                    if test_result["success"]:

                        output.append(
                            "TEST STATUS: SUCCESS"
                        )

                    else:

                        output.append(
                            "TEST STATUS: FAILED"
                        )

                    output.append("")

                    if test_result.get("output"):

                        output.append(
                            test_result["output"]
                        )

                output.append("")

                output.append(
                    "========== FINAL RESULT =========="
                )

                output.append("")

                output.append(
                    "PROJECT UPDATE SUCCESSFUL"
                )

            else:

                output.append(
                    "STATUS: PROJECT UPDATE FAILED"
                )

                output.append("")

                if result.get("message"):

                    output.append(
                        str(
                            result["message"]
                        )
                    )

                output.append("")

                output.append(
                    "========== DEVELOPMENT LOG =========="
                )

                output.append("")

                for item in result.get(
                    "history",
                    []
                ):

                    output.append(
                        str(item)
                    )

            return "\n".join(
                output
            )

        # =================================
        # NORMAL DEVELOP
        # =================================

        result = self.executor.execute(
            request
        )

        output = []

        output.append(
            "========== AZAD DEVELOPER =========="
        )

        output.append("")

        if result["success"]:

            output.append(
                "STATUS: SUCCESS"
            )

            output.append("")

            output.append(
                f"File: {result['filepath']}"
            )

            output.append("")

            output.append(
                "========== OUTPUT =========="
            )

            output.append("")

            output.append(
                str(result["output"])
            )

        else:

            output.append(
                "STATUS: FAILED"
            )

            output.append("")

            if "filepath" in result:

                output.append(
                    f"File: {result['filepath']}"
                )

            output.append("")

            output.append(
                "========== RESULT =========="
            )

            output.append("")

            output.append(
                str(
                    result.get(
                        "output",
                        result.get(
                            "message",
                            "Unknown error."
                        )
                    )
                )
            )

        output.append("")

        output.append(
            "========== DEVELOPMENT LOG =========="
        )

        output.append("")

        for item in result.get(
            "history",
            []
        ):

            output.append(
                str(item)
            )

        return "\n".join(
            output
        )

    # =================================
    # FIX
    # =================================

    def handle_fix(
        self,
        message
    ):

        filepath = message[
            4:
        ].strip()

        if not filepath:

            return (
                "Please provide a file path.\n"
                "Example: fix workspace/generated.py"
            )

        result = (
            self.executor.fix_existing_file(
                filepath
            )
        )

        output = []

        output.append(
            "========== AZAD AUTO FIX =========="
        )

        output.append("")

        if result["success"]:

            output.append(
                "STATUS: FIXED"
            )

            output.append("")

            output.append(
                f"File: {result['filepath']}"
            )

            output.append("")

            output.append(
                "========== OUTPUT =========="
            )

            output.append("")

            output.append(
                str(result["output"])
            )

        else:

            output.append(
                "STATUS: FAILED"
            )

            output.append("")

            output.append(
                str(
                    result.get(
                        "output",
                        result.get(
                            "message",
                            "Unknown error."
                        )
                    )
                )
            )

        output.append("")

        output.append(
            "========== FIX LOG =========="
        )

        output.append("")

        for item in result.get(
            "history",
            []
        ):

            output.append(
                str(item)
            )

        return "\n".join(
            output
        )

    # =================================
    # SELF IMPROVEMENT
    # =================================

    def handle_improve(
        self,
        message
    ):

        request = message[
            len("improve"):
        ].strip()

        if not request:

            request = (
                "Improve AZAD safely. "
                "Find one useful improvement "
                "to the existing architecture."
            )

        result = self.self_improver.improve(
            request
        )

        output = []

        output.append(
            "========== AZAD SELF IMPROVEMENT =========="
        )

        output.append("")

        if result["success"]:

            output.append(
                "STATUS: SUCCESS"
            )

        else:

            output.append(
                "STATUS: FAILED"
            )

        output.append("")

        output.append(
            "========== EVOLUTION LOG =========="
        )

        output.append("")

        for item in result.get(
            "history",
            []
        ):

            output.append(
                str(item)
            )

        output.append("")

        if result.get("changed"):

            output.append(
                "AZAD successfully improved its code."
            )

        else:

            output.append(
                result.get(
                    "message",
                    "No change was necessary."
                )
            )

        if result.get("test_result"):

            output.append("")

            output.append(
                "========== FINAL TEST =========="
            )

            output.append("")

            test_result = result[
                "test_result"
            ]

            if test_result["success"]:

                output.append(
                    "TEST STATUS: SUCCESS"
                )

            else:

                output.append(
                    "TEST STATUS: FAILED"
                )

        return "\n".join(
            output
        )

    # =================================
    # ANALYZE PROJECT
    # =================================

    def _analyze_project(
        self,
        directory
    ):

        analysis = (
            self.project_analyzer.analyze(
                directory
            )
        )

        project_name = analysis[
            "project"
        ]

        memory_key = (
            "project:"
            + project_name
        )

        self.memory.save(
            memory_key,
            analysis
        )

        return analysis

    # =================================
    # BUILD PROJECT
    # =================================

    def handle_build(
        self,
        message
    ):

        request = message[
            6:
        ].strip()

        if not request:

            return (
                "Please describe the project "
                "you want to build."
            )

        output = []

        output.append(
            "========== AZAD PROJECT BUILDER =========="
        )

        output.append("")
        output.append(
            "Building project..."
        )
        output.append("")

        result = self.project_builder.build(
            request
        )

        if not result["success"]:

            output.append(
                "STATUS: FAILED"
            )

            output.append("")

            output.append(
                str(
                    result.get(
                        "message",
                        "Project build failed."
                    )
                )
            )

            return "\n".join(output)

        output.append(
            "STATUS: PROJECT CREATED"
        )

        output.append("")

        output.append(
            f"Project: {result['project']}"
        )

        output.append(
            f"Directory: {result['directory']}"
        )

        output.append("")

        output.append(
            "========== FILES =========="
        )

        output.append("")

        for filepath in result["files"]:

            output.append(filepath)

        output.append("")

        # =================================
        # TEST
        # =================================

        output.append(
            "========== TESTING =========="
        )

        output.append("")

        test_result = (
            self.project_tester.test_project(
                result["directory"]
            )
        )

        if test_result["success"]:

            output.append(
                "TEST STATUS: SUCCESS"
            )

        else:

            output.append(
                "TEST STATUS: FAILED"
            )

            output.append("")

            if test_result["output"]:

                output.append(
                    test_result["output"]
                )

            output.append("")

            output.append(
                "========== AUTO FIX =========="
            )

            output.append("")

            fix_result = (
                self.auto_fixer.fix_project(
                    result["directory"],
                    test_result
                )
            )

            for item in fix_result.get(
                "history",
                []
            ):

                output.append(
                    str(item)
                )

            test_result = (
                fix_result["test_result"]
            )

            output.append("")

            if not fix_result["success"]:

                output.append(
                    "========== FINAL RESULT =========="
                )

                output.append("")

                output.append(
                    "PROJECT BUILD FAILED"
                )

                output.append("")

                output.append(
                    "Maximum Auto-Fix attempts "
                    "reached or the error could "
                    "not be fixed."
                )

                output.append("")

                output.append(
                    f"Attempts: "
                    f"{fix_result['attempts']}"
                )

                return "\n".join(output)

        # =================================
        # PROJECT ANALYSIS
        # =================================

        output.append("")

        output.append(
            "========== PROJECT ANALYSIS =========="
        )

        output.append("")

        try:

            analysis = (
                self._analyze_project(
                    result["directory"]
                )
            )

            output.append(
                "PROJECT ANALYSIS: SUCCESS"
            )

            output.append("")

            output.append(
                f"Files analyzed: "
                f"{analysis['file_count']}"
            )

            output.append(
                f"Tests detected: "
                f"{analysis['test_count']}"
            )

            output.append(
                f"Classes: "
                f"{len(analysis['classes'])}"
            )

            output.append(
                f"Functions: "
                f"{len(analysis['functions'])}"
            )

            output.append("")

            output.append(
                "Project purpose:"
            )

            output.append(
                analysis["purpose"]
            )

        except Exception as e:

            output.append(
                "PROJECT ANALYSIS: FAILED"
            )

            output.append("")

            output.append(
                str(e)
            )

        output.append("")

        output.append(
            "========== FINAL RESULT =========="
        )

        output.append("")

        output.append(
            "PROJECT BUILD SUCCESSFUL"
        )

        return "\n".join(output)

    # =================================
    # MAIN HANDLE
    # =================================

    def handle(
        self,
        message
    ):

        message = message.strip()

        lower = message.lower()

        # =================================
        # BUILD
        # =================================

        if lower.startswith("build "):

            return self.handle_build(
                message
            )

        # =================================
        # DEVELOP
        # =================================

        if lower.startswith("develop "):

            return self.handle_develop(
                message
            )

        # =================================
        # FIX
        # =================================

        if lower.startswith("fix "):

            return self.handle_fix(
                message
            )

        # =================================
        # IMPROVE
        # =================================

        if (
            lower == "improve"
            or lower.startswith("improve ")
        ):

            return self.handle_improve(
                message
            )

        return None