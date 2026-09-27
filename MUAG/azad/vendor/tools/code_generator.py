class CodeGenerator:

    def __init__(self, ai):
        self.ai = ai

    def generate(self, request):

        prompt = f"""
You are an expert Python developer.

Rules:
- Return ONLY valid Python code.
- Do NOT use markdown.
- Do NOT use ```python or ```.
- Do NOT explain anything.
- Output only executable Python code.

Task:
{request}
"""

        code = self.ai.ask(prompt).strip()

        # Remove markdown if AI still returns it
        if code.startswith("```python"):
            code = code.replace("```python", "", 1)

        if code.startswith("```"):
            code = code.replace("```", "", 1)

        if code.endswith("```"):
            code = code[:-3]

        return code.strip()