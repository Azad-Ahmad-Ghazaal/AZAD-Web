from tools.code_generator import CodeGenerator
from tools.write_file import WriteFileTool
from tools.python_runner import PythonRunner


class Developer:

    def __init__(self, ai):

        self.generator = CodeGenerator(ai)
        self.writer = WriteFileTool()
        self.runner = PythonRunner()

    def develop(self, request):

        code = self.generator.generate(request)

        filepath = "workspace/generated.py"

        self.writer.write(filepath, code)

        result = self.runner.run(filepath)

        return (
            "========== GENERATED CODE ==========\n\n"
            + code +
            "\n\n========== OUTPUT ==========\n\n"
            + result
        )