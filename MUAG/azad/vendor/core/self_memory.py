import os
import json

class SelfMemoryEngine:
    def __init__(self, memory_file="data/azad_memory.json"):
        self.memory_file = memory_file
        self.ensure_memory_file()

    def ensure_memory_file(self):
        if not os.path.exists(self.memory_file):
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump({"learned_patterns": [], "context_history": []}, f)

    def record_learning(self, user_input, ai_response):
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            data["context_history"].append({"user": user_input, "azad": ai_response})
            
            if len(data["context_history"]) > 50:
                data["context_history"] = data["context_history"][-50:]
                
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Memory recording error: {e}")