from tools.read_file import ReadFileTool


class CodeAnalyzer:

    def __init__(self, ai):
        self.ai = ai
        self.reader = ReadFileTool()

    def analyze(self, filepath):

        code = self.reader.read(filepath)

        if code.startswith("File not found") or code.startswith("Error"):
            return code

        prompt = f"""
You are a senior Python software engineer.

Analyze this Python file.

Explain:

1. Purpose
2. Classes
3. Functions
4. Problems
5. Improvements

Python Code:

{code}
"""

        return self.ai.ask(prompt)