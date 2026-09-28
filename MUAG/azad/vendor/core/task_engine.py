import json
import os
from datetime import datetime


class TaskEngine:

    def __init__(self, ai=None):

        self.ai = ai

        self.tasks = []

        self.task_file = "data/tasks.json"

        self._load_tasks()

    # =================================
    # LOAD TASKS
    # =================================

    def _load_tasks(self):

        try:

            if os.path.exists(self.task_file):

                with open(
                    self.task_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    self.tasks = json.load(file)

            else:

                self.tasks = []

        except Exception:

            self.tasks = []

    # =================================
    # SAVE TASKS
    # =================================

    def _save_tasks(self):

        try:

            folder = os.path.dirname(
                self.task_file
            )

            if folder:

                os.makedirs(
                    folder,
                    exist_ok=True
                )

            with open(
                self.task_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.tasks,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            return True

        except Exception:

            return False

    # =================================
    # CREATE TASK
    # =================================

    def create_task(self, description):

        description = str(
            description
        ).strip()

        if not description:

            return {
                "success": False,
                "message": "Task description is empty."
            }

        next_id = 1

        if self.tasks:

            next_id = max(
                task.get("id", 0)
                for task in self.tasks
            ) + 1

        task = {

            "id": next_id,

            "description": description,

            "status": "pending",

            "created": datetime.now().isoformat(),

            "started": None,

            "completed": None,

            "steps": [],

            "result": None
        }

        self.tasks.append(task)

        self._save_tasks()

        return {
            "success": True,
            "task": task
        }

    # =================================
    # GET TASK
    # =================================

    def get_task(self, task_id):

        for task in self.tasks:

            if task.get("id") == task_id:

                return task

        return None

    # =================================
    # UPDATE TASK
    # =================================

    def update_task(
        self,
        task_id,
        status=None,
        result=None
    ):

        task = self.get_task(
            task_id
        )

        if task is None:

            return False

        if status is not None:

            task["status"] = str(
                status
            )

        if result is not None:

            task["result"] = self._safe_text(
                result
            )

        if status == "running":

            task["started"] = (
                datetime.now().isoformat()
            )

        if status == "completed":

            task["completed"] = (
                datetime.now().isoformat()
            )

        self._save_tasks()

        return True

    # =================================
    # ADD STEP
    # =================================

    def add_step(
        self,
        task_id,
        step
    ):

        task = self.get_task(
            task_id
        )

        if task is None:

            return False

        task["steps"].append({

            "step": self._safe_text(
                step
            ),

            "status": "pending",

            "created": datetime.now().isoformat(),

            "completed": None,

            "result": None
        })

        self._save_tasks()

        return True

    # =================================
    # UPDATE STEP
    # =================================

    def update_step(
        self,
        task_id,
        step_index,
        status=None,
        result=None
    ):

        task = self.get_task(
            task_id
        )

        if task is None:

            return False

        if step_index < 0:

            return False

        if step_index >= len(
            task["steps"]
        ):

            return False

        step = task["steps"][
            step_index
        ]

        if status is not None:

            step["status"] = str(
                status
            )

        if result is not None:

            step["result"] = self._safe_text(
                result
            )

        if status == "completed":

            step["completed"] = (
                datetime.now().isoformat()
            )

        self._save_tasks()

        return True

    # =================================
    # SAFE TEXT
    # =================================

    def _safe_text(self, value):

        if value is None:

            return ""

        if isinstance(
            value,
            str
        ):

            return value

        if isinstance(
            value,
            dict
        ):

            try:

                return json.dumps(
                    value,
                    indent=2,
                    ensure_ascii=False
                )

            except Exception:

                return str(value)

        if isinstance(
            value,
            list
        ):

            try:

                return json.dumps(
                    value,
                    indent=2,
                    ensure_ascii=False
                )

            except Exception:

                return str(value)

        return str(value)

    # =================================
    # PLAN
    # =================================

    def plan(self, description):

        if self.ai is None:

            return [
                description
            ]

        prompt = f"""
You are AZAD Task Planner.

Break the following task into practical
development steps.

IMPORTANT:

1. Return ONLY a numbered list.
2. Do not write code.
3. Do not write explanations.
4. Keep the number of steps reasonable.
5. Do not turn every single Python line
   into a separate task.
6. A complete program should normally
   be handled as ONE development step.

Task:

{description}
"""

        try:

            response = self.ai.ask(
                prompt
            )

            response = self._safe_text(
                response
            )

            lines = response.splitlines()

            steps = []

            for line in lines:

                line = line.strip()

                if not line:

                    continue

                # Remove common numbering

                if len(line) > 1:

                    if (
                        line[0].isdigit()
                        and line[1] in ".-)"
                    ):

                        line = line[2:].strip()

                if line:

                    steps.append(line)

            if not steps:

                return [
                    description
                ]

            return steps

        except Exception:

            return [
                description
            ]

    # =================================
    # START TASK
    # =================================

    def start_task(
        self,
        description
    ):

        created = self.create_task(
            description
        )

        if not created["success"]:

            return created

        task = created["task"]

        steps = self.plan(
            description
        )

        for step in steps:

            self.add_step(
                task["id"],
                step
            )

        self.update_task(
            task["id"],
            status="planned"
        )

        return {
            "success": True,
            "task": self.get_task(
                task["id"]
            )
        }

    # =================================
    # EXECUTE TASK
    # =================================

    def execute_task(
        self,
        task_id,
        developer_agent
    ):

        task = self.get_task(
            task_id
        )

        if task is None:

            return {
                "success": False,
                "message": "Task not found.",
                "log": []
            }

        self.update_task(
            task_id,
            status="running"
        )

        execution_log = []

        # ---------------------------------
        # Execute Steps
        # ---------------------------------

        for index, step in enumerate(
            task["steps"]
        ):

            self.update_step(
                task_id,
                index,
                status="running"
            )

            step_text = self._safe_text(
                step.get("step", "")
            )

            execution_log.append(
                f"Step {index + 1}: {step_text}"
            )

            try:

                command = (
                    "develop "
                    + step_text
                )

                result = developer_agent.handle(
                    command
                )

                # ---------------------------------
                # Normalize Developer Result
                # ---------------------------------

                result_text = self._safe_text(
                    result
                )

                if not result_text:

                    result_text = (
                        "Developer Agent returned "
                        "an empty result."
                    )

                # ---------------------------------
                # Check Failure
                # ---------------------------------

                failed = (
                    "STATUS: FAILED"
                    in result_text.upper()
                )

                if failed:

                    self.update_step(
                        task_id,
                        index,
                        status="failed",
                        result=result_text
                    )

                    self.update_task(
                        task_id,
                        status="failed",
                        result=result_text
                    )

                    execution_log.append(
                        f"Step {index + 1}: FAILED"
                    )

                    return {
                        "success": False,
                        "task": self.get_task(
                            task_id
                        ),
                        "log": execution_log,
                        "result": result_text
                    }

                # ---------------------------------
                # Success
                # ---------------------------------

                self.update_step(
                    task_id,
                    index,
                    status="completed",
                    result=result_text
                )

                execution_log.append(
                    f"Step {index + 1}: COMPLETED"
                )

            except Exception as e:

                error = str(e)

                self.update_step(
                    task_id,
                    index,
                    status="failed",
                    result=error
                )

                self.update_task(
                    task_id,
                    status="failed",
                    result=error
                )

                execution_log.append(
                    f"Step {index + 1}: ERROR - {error}"
                )

                return {
                    "success": False,
                    "task": self.get_task(
                        task_id
                    ),
                    "log": execution_log,
                    "result": error
                }

        # ---------------------------------
        # Task Complete
        # ---------------------------------

        final_result = (
            "All task steps completed successfully."
        )

        self.update_task(
            task_id,
            status="completed",
            result=final_result
        )

        execution_log.append(
            "TASK COMPLETED"
        )

        return {
            "success": True,
            "task": self.get_task(
                task_id
            ),
            "log": execution_log,
            "result": final_result
        }

    # =================================
    # LIST TASKS
    # =================================

    def list_tasks(self):

        return self.tasks

    # =================================
    # FORMAT TASK
    # =================================

    def format_task(
        self,
        task
    ):

        if task is None:

            return "Task not found."

        output = []

        output.append(
            "========== AZAD TASK =========="
        )

        output.append("")

        output.append(
            f"Task #{task['id']}"
        )

        output.append(
            f"Description: "
            f"{task['description']}"
        )

        output.append(
            f"Status: {task['status']}"
        )

        output.append("")

        output.append(
            "Steps:"
        )

        for index, step in enumerate(
            task["steps"],
            start=1
        ):

            step_name = self._safe_text(
                step.get(
                    "step",
                    ""
                )
            )

            step_status = self._safe_text(
                step.get(
                    "status",
                    ""
                )
            )

            output.append(
                f"{index}. "
                f"{step_name} "
                f"[{step_status}]"
            )

        output.append("")

        output.append(
            "=============================="
        )

        return "\n".join(
            output
        )

    # =================================
    # FORMAT EXECUTION
    # =================================

    def format_execution(
        self,
        result
    ):

        output = []

        output.append(
            "========== AZAD TASK EXECUTION =========="
        )

        output.append("")

        if result.get("success"):

            output.append(
                "STATUS: SUCCESS"
            )

        else:

            output.append(
                "STATUS: FAILED"
            )

        output.append("")

        for item in result.get(
            "log",
            []
        ):

            output.append(
                self._safe_text(item)
            )

        output.append("")

        final_result = result.get(
            "result",
            ""
        )

        if final_result:

            output.append(
                "RESULT:"
            )

            output.append(
                self._safe_text(
                    final_result
                )
            )

            output.append("")

        output.append(
            "=========================================="
        )

        return "\n".join(
            output
        )