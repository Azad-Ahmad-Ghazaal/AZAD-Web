# agent/desktop_agent.py

import os
import subprocess

class DesktopAgent:
    def __init__(self):
        print("[DesktopAgent] Initialized - Ready to control system tasks.")

    def handle(self, message):
        msg_lower = message.lower()
        
        # 1. Open Notepad or applications
        if "open notepad" in msg_lower:
            try:
                subprocess.Popen(["notepad.exe"])
                return "Successfully opened Notepad on your laptop."
            except Exception as e:
                return f"Failed to open Notepad: {e}"
                
        # 2. Run a terminal command or script
        elif msg_lower.startswith("run cmd "):
            cmd = message[8:].strip()
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                output = result.stdout if result.stdout else result.stderr
                return f"Command executed successfully.\nOutput:\n{output}"
            except Exception as e:
                return f"Error executing command: {e}"
                
        # 3. List files in a directory
        elif msg_lower.startswith("list files"):
            try:
                files = os.listdir(".")
                return f"Files in current directory:\n" + "\n".join(files)
            except Exception as e:
                return f"Error listing files: {e}"
                
        return None