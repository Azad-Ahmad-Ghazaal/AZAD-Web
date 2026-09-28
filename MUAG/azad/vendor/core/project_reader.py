import os


class ProjectReader:

    def __init__(self, root="D:\\Azad"):
        self.root = root

        self.ignore_folders = [
            "venv",
            "__pycache__",
            ".git",
            ".idea",
            ".vscode"
        ]

    def get_project_files(self):

        files = []

        for folder, _, filenames in os.walk(self.root):

            skip = False

            for ignored in self.ignore_folders:
                if ignored in folder:
                    skip = True
                    break

            if skip:
                continue

            for filename in filenames:

                if filename.endswith(".py"):
                    files.append(os.path.join(folder, filename))

        return files

    def summarize(self):

        files = self.get_project_files()

        result = "===== AZAD PROJECT =====\n\n"

        for file in files:
            result += file + "\n"

        result += f"\n\nTotal Python Files: {len(files)}"

        return result