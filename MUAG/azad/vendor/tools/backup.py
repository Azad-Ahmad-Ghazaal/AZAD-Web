from pathlib import Path
from datetime import datetime
import shutil


class BackupTool:

    def backup(self, filepath):

        try:

            source = Path(filepath)

            if not source.exists():
                return "File not found."

            backup_folder = Path("backups")

            backup_folder.mkdir(exist_ok=True)

            filename = source.stem

            extension = source.suffix

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            backup_file = backup_folder / f"{filename}_{timestamp}{extension}"

            shutil.copy2(source, backup_file)

            return f"Backup Created: {backup_file}"

        except Exception as e:

            return f"Error: {e}"