import os
import re

from agent.desktop_agent import DesktopAgent
from agent.developer_agent import DeveloperAgent
from agent.file_agent import FileAgent
from tools.voice_tool import VoiceTool
from tools.self_improver import SelfImprover
from core.memory import Memory
from core.decision import DecisionEngine
from core.skill_manager import SkillManager
from core.ai_engine import AIEngine
from core.task_engine import TaskEngine
from core.self_evolution import SelfEvolutionEngine
from core.agent_gateway import AZADAgentGateway
from core.listening_runtime import AZADListeningRuntime
from core.model_lab import AZADModelLab
from core.model_registry import AZADModelRegistry
from training.benchmark import AZADBenchmarkRunner
from training.ollama_backend import AZADOllamaBackend
from training.model_release import AZADModelRelease
from tools.desktop_runtime import DesktopToolRuntime
from skills.calculator import Calculator
from skills.notes import Notes
from tools.code_analyzer import CodeAnalyzer
from tools.code_generator import CodeGenerator


class AZAD:
    def __init__(self):
        self.name = "AZAD"
        self.status = "Starting"
        self.memory = Memory()
        self.skills = SkillManager()
        self.ai = AIEngine()
        self.task_engine = TaskEngine(self.ai)
        self.voice = VoiceTool()
        self.analyzer = CodeAnalyzer(self.ai)
        self.generator = CodeGenerator(self.ai)
        self.developer_agent = DeveloperAgent(self.ai)
        self.file_agent = FileAgent()
        self.desktop_agent = DesktopAgent()
        self.desktop_runtime = DesktopToolRuntime(self.desktop_agent)
        self.evolution_engine = SelfEvolutionEngine()
        self.self_improver = SelfImprover(self.ai, self.developer_agent.project_tester, self.analyzer, self.memory)
        self.skills.register("calculator", Calculator())
        self.skills.register("notes", Notes())
        self.decision = DecisionEngine(self.skills)
        self.agent_gateway = AZADAgentGateway(
            memory=self.memory,
            ai_engine=self.ai,
            desktop_runtime=self.desktop_runtime,
            mcp_config=os.getenv("AZAD_MCP_CONFIG") or None,
        )
        self.listening = AZADListeningRuntime(duration_seconds=120.0)
        self.model_lab = AZADModelLab()
        self.model_registry = AZADModelRegistry()
        self.model_benchmark = AZADBenchmarkRunner()
        self.model_release = AZADModelRelease(self.model_lab, self.model_registry)

    def start(self):
        self.status = "Online"
        print("==============================")
        print("        AZAD AI CORE")
        print("==============================")
        print("Status:", self.status)
        print("AI Model:", self.ai.model)
        print("Task Engine: Active")
        print("Developer Agent: Active")
        print("File Agent: Active")
        print("Voice Agent: Active")
        print("Desktop Agent: Active")
        print("Self-Evolution Engine: Active")
        print("Self-Improver: Active")
        print("Autonomous Agent Runtime: Active")
        print("Memory-Aware Agent Runtime: Active")
        print("Native AI Bot: Active")
        print("MCP Runtime: Active" if os.getenv("AZAD_MCP_CONFIG") else "MCP Runtime: Standby")
        print("Listening Runtime: Active")
        print("AZAD Model Lab: Active")
        print("==============================")

    def _clean_code_response(self, code):
        if not code:
            return ""
        code = code.strip()
        if code.startswith("```python"):
            code = code[len("```python"):]
        elif code.startswith("```"):
            code = code[len("```"):]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip()

    def _handle_evolution_command(self, message, should_speak=False):
        raw_data = message[7:].strip()
        if not raw_data:
            return "Please provide a file and new Python code.\n\nExample:\nevolve core/example.py | print('Hello')"
        parts = raw_data.split("|", 1)
        if len(parts) != 2:
            return "Invalid evolution format.\n\nUse:\nevolve core/example.py | [new python code]"
        file_path = parts[0].replace("EDIT:", "").strip()
        new_code = self._clean_code_response(parts[1].strip())
        if not file_path:
            return "Evolution failed: file path is missing."
        if not new_code:
            return "Evolution failed: new code is empty."
        result = self.evolution_engine.modify_code(file_path, new_code)
        success = result.get("success", False) if isinstance(result, dict) else bool(result)
        if success:
            response = f"========== AZAD SELF-EVOLUTION ==========\n\nSTATUS: SUCCESS\n\nFile: {file_path}\n\nCode was modified safely.\nBackup created.\nSyntax validation passed."
        else:
            message_text = result.get("message", "Modification failed.") if isinstance(result, dict) else "Modification failed."
            response = f"========== AZAD SELF-EVOLUTION ==========\n\nSTATUS: FAILED\n\nFile: {file_path}\n\nReason: {message_text}"
        if should_speak:
            self.voice.speak("Self evolution completed successfully." if success else "Self evolution failed.")
        return response

    def _handle_self_improvement(self, message, should_speak=False):
        request = message[len("improve"):].strip() or "Improve AZAD safely. Find one useful improvement without removing existing features."
        result = self.self_improver.improve(request)
        output = ["========== AZAD SELF-IMPROVEMENT ==========", "", "STATUS: SUCCESS" if result.get("success", False) else "STATUS: FAILED", ""]
        output.append("AZAD code was improved." if result.get("changed", False) else "No code change was made.")
        output.extend(["", "========== IMPROVEMENT LOG ==========", ""])
        output.extend(str(item) for item in result.get("history", []))
        changes = result.get("changes", [])
        if changes:
            output.extend(["", "========== MODIFIED FILES ==========", ""])
            output.extend(str(change.get("file", "Unknown")) for change in changes)
        test_result = result.get("test_result")
        if test_result:
            output.extend(["", "========== TEST RESULT ==========", "", "TEST STATUS: SUCCESS" if test_result.get("success", False) else "TEST STATUS: FAILED", ""])
            if test_result.get("output"):
                output.append(str(test_result["output"]))
        if result.get("message"):
            output.extend(["", "Message:", str(result["message"])])
        output.extend(["", "========== FINAL RESULT ==========", "", "SELF-IMPROVEMENT COMPLETED" if result.get("success", False) and result.get("changed", False) else "NO IMPROVEMENT REQUIRED" if result.get("success", False) else "SELF-IMPROVEMENT FAILED"])
        response = "\n".join(output)
        if should_speak:
            self.voice.speak("Self improvement process completed.")
        return response

    def _record_model_experience(self, request, response, *, success, verified=False, source="azad", tool=None, category="general", feedback=None):
        return self.model_lab.record_experience(
            request, str(response), success=bool(success), verified=bool(verified),
            source=source, tool=tool, category=category, feedback=feedback,
        )

    def _autonomous_handle(self, message, should_speak=False):
        try:
            result = self.agent_gateway.handle(message)
            if not result.get("results") or not result.get("success"):
                return None
            results = result["results"]
            last = results[-1] if results else {}
            response = last.get("message") or result.get("data") or "Task completed by AZAD Agent Runtime."
            if isinstance(response, (dict, list)):
                response = str(response)
            self.listening.add_assistant_text(str(response))
            self.model_lab.record_experience(
                message,
                str(response),
                success=True,
                verified=True,
                source="agent_runtime",
                tool=str(last.get("tool_name") or last.get("tool") or last.get("name") or "agent_runtime"),
                category="tool_use",
            )
            if should_speak:
                self.voice.speak(str(response))
            return str(response)
        except Exception as exc:
            print(f"[AZAD AGENT RUNTIME] fallback: {exc}")
        return None

    def talk(self, message):
        message = self.listening.resolve_request(message)
        if not message:
            return "Please enter a command."
        self.listening.add_user_text(message)
        should_speak = False
        if message.lower().startswith("speak:"):
            should_speak = True
            message = message[6:].strip()
        lower = message.lower()

        if lower in {"model registry", "model registry status", "models"}:
            return str(self.model_registry.list_models())
        if lower in {"model active", "active model"}:
            return str(self.model_registry.get_active())
        if lower in {"model benchmark", "benchmark model", "model benchmark local", "benchmark local model"}:
            try:
                backend = AZADOllamaBackend(self.ai.model)
                return str(self.model_benchmark.run(backend))
            except Exception as exc:
                return str({
                    "status": "backend_error",
                    "passed": False,
                    "score": None,
                    "error": str(exc),
                })
        if lower.startswith("model train "):
            raw = message[len("model train "):].strip()
            parts = raw.split(None, 1)
            if len(parts) != 2:
                return "Use: model train <model_id>:<version> <huggingface_base_model>"
            target, base_model = parts[0].strip(), parts[1].strip()
            id_parts = target.split(":", 1)
            if not id_parts[0] or (len(id_parts) == 2 and not id_parts[1]):
                return "Use: model train <model_id>:<version> <huggingface_base_model>"
            model_id = id_parts[0]
            version = id_parts[1] if len(id_parts) == 2 else "0.1.0"
            try:
                return str(self.model_release.train_candidate(
                    model_id=model_id,
                    version=version,
                    base_model=base_model,
                ))
            except Exception as exc:
                return f"Model training failed: {exc}"

        if lower.startswith("model release "):
            raw = message[len("model release "):].strip()
            parts = raw.split(":", 1)
            if not raw or not parts[0].strip() or (len(parts) == 2 and not parts[1].strip()):
                return "Use: model release <model_id>:<version>"
            model_id = parts[0].strip()
            version = parts[1].strip() if len(parts) == 2 else "0.1.0"
            return str(self.model_release.create_candidate(
                model_id=model_id,
                version=version,
                base_model=self.ai.model,
                backend="ollama",
            ))
        if lower.startswith("model activate "):
            raw = message[len("model activate "):].strip()
            parts = raw.split(":", 1)
            try:
                model_id = parts[0].strip()
                version = parts[1].strip() if len(parts) == 2 else None
                active = self.model_registry.set_active(model_id, version)
                self.ai.set_model(active["base_model"])
                return str(active)
            except (KeyError, ValueError) as exc:
                return f"Model activation blocked: {exc}"
        if lower.startswith("model candidate approve "):
            raw = message[len("model candidate approve "):].strip()
            parts = raw.split(":", 1)
            try:
                model_id = parts[0].strip()
                version = parts[1].strip() if len(parts) == 2 else None
                return str(self.model_registry.approve(model_id, version))
            except (KeyError, ValueError) as exc:
                return f"Model approval blocked: {exc}"
        if lower in {"model lab", "model status", "model lab status"}:
            return str(self.model_lab.status())
        if lower in {"model pending", "model lab pending"}:
            return str(self.model_lab.pending())
        if lower in {"prepare model dataset", "build model dataset"}:
            return str(self.model_lab.prepare_verified_dataset())
        if lower.startswith("model approve "):
            try:
                index = int(message[len("model approve "):].strip())
            except ValueError:
                return "Use: model approve <index>"
            return "Model experience approved." if self.model_lab.approve_experience(index) else "Invalid model experience index."
        if lower.startswith("model reject "):
            try:
                index = int(message[len("model reject "):].strip())
            except ValueError:
                return "Use: model reject <index>"
            return "Model experience rejected." if self.model_lab.reject_experience(index) else "Invalid model experience index."
        if lower.startswith("model correct "):
            raw = message[len("model correct "):].strip()
            parts = raw.split("|", 1)
            if len(parts) != 2 or not parts[1].strip():
                return "Use: model correct <index> | corrected response"
            try:
                index = int(parts[0].strip())
            except ValueError:
                return "Use: model correct <index> | corrected response"
            return "Model experience corrected and approved." if self.model_lab.correct_experience(index, parts[1].strip()) else "Invalid model experience index."

        if lower == "improve" or lower == "improve yourself" or lower.startswith("improve "):
            return self._handle_self_improvement(message, should_speak)
        if "brain.py" in lower and ("code" in lower or "uth" in lower or "dikh" in lower or "give" in lower):
            try:
                with open("core/brain.py", "r", encoding="utf-8") as f:
                    response = "core/brain.py |\n```python\n" + f.read() + "\n```"
            except Exception as e:
                response = "Error reading brain.py: " + str(e)
            if should_speak:
                self.voice.speak("Yeh lijiye aapka brain file ka code.")
            return response
        if lower.startswith("evolve "):
            return self._handle_evolution_command(message, should_speak)
        if lower.startswith("task "):
            description = message[5:].strip()
            if not description:
                return "Please describe the task.\nExample:\ntask create a Python calculator"
            result = self.task_engine.start_task(description)
            if not result.get("success", False):
                return result.get("message", "Could not create task.")
            task = result["task"]
            execution = self.task_engine.execute_task(task["id"], self.developer_agent)
            response = self.task_engine.format_task(execution["task"]) + "\n\n" + self.task_engine.format_execution(execution)
            self._record_model_experience(
                description, response, success=bool(execution.get("success", False)),
                verified=bool(execution.get("success", False)),
                source="task_engine", category="task_execution",
            )
            if should_speak:
                self.voice.speak("Task mukammal ho gaya hai.")
            return response
        try:
            plan = self.agent_gateway.inspect(message)
            if plan.get("intent") in {"desktop_tool", "mcp_tool"}:
                autonomous = self._autonomous_handle(message, should_speak)
                if autonomous is not None:
                    return autonomous
        except Exception as exc:
            print(f"[AZAD AGENT RUNTIME] tool routing fallback: {exc}")

        result = self.developer_agent.handle(message)
        if result is not None:
            self._record_model_experience(message, result, success=True, source="developer_agent", category="coding")
            if should_speak:
                self.voice.speak("Developer agent ne kaam kar diya hai.")
            return result
        result = self.desktop_agent.handle(message)
        if result is not None:
            self._record_model_experience(message, result, success=True, source="desktop_agent", category="desktop")
            if should_speak:
                self.voice.speak("Desktop agent ne task perform kar diya hai.")
            return result
        result = self.file_agent.handle(message)
        if result is not None:
            self._record_model_experience(message, result, success=True, source="file_agent", category="file")
            if should_speak:
                self.voice.speak("File agent active hai.")
            return result
        if lower.startswith("analyze "):
            return self.analyzer.analyze(message[8:].strip())
        if lower.startswith("code "):
            return self.generator.generate(message[5:].strip())
        if message.startswith("/"):
            return self.decision.process(message)
        autonomous = self._autonomous_handle(message, should_speak)
        if autonomous is not None:
            return autonomous
        context_prompt = self.listening.build_context(message)
        response = self.ai.ask(message, system_prompt=(
            "You are AZAD. Use recent conversation context only when it helps resolve references "
            "such as this, that, it, they, or previous requests. Do not repeat the context verbatim.\n"
            + context_prompt
        ))
        if response and ".py" in response and "|" in response:
            try:
                match = re.search(r'([^\s|]+\.py)\s*\|\s*(.*)', response, re.DOTALL)
                if match:
                    file_path = match.group(1).strip()
                    file_code = self._clean_code_response(match.group(2).strip())
                    evolution_result = self.evolution_engine.modify_code(file_path, file_code)
                    saved = evolution_result.get("success", False) if isinstance(evolution_result, dict) else bool(evolution_result)
                    if saved:
                        response += f"\n\n[System Note: Automatically detected and safely saved file -> {file_path}]"
            except Exception as e:
                response += f"\n\n[System Note: Automatic file handling failed: {e}]"
        self.listening.add_assistant_text(response)
        self._record_model_experience(
            message, response, success=bool(response), verified=False,
            source="ai_engine", category="conversation",
        )
        if should_speak:
            self.voice.speak(response)
        return response
