import shutil
import time
from pathlib import Path


class SelfEvolutionEngine:

    def __init__(self):
        self.root_dir = Path(".").resolve()

        self.backup_dir = (
            self.root_dir
            / "backups"
            / "self_evolution"
        )

        self.backup_dir.mkdir(
            exist_ok=True,
            parents=True
        )

        self.protected_directories = {
            "venv",
            ".git",
            "__pycache__",
            "workspace",
            "backups"
        }

        self.protected_files = {
            ".env",
            "memory.json"
        }

    # =========================================
    # SECURITY
    # =========================================

    def _is_safe_target(self, file_path):
        try:
            target = Path(file_path).resolve()

            target.relative_to(self.root_dir)

        except ValueError:
            return False

        for parent in target.parents:
            if parent.name in self.protected_directories:
                return False

        if target.name in self.protected_files:
            return False

        return True

    # =========================================
    # BACKUP
    # =========================================

    def _create_backup(self, target):

        timestamp = time.strftime(
            "%Y%m%d_%H%M%S"
        )

        relative = target.relative_to(
            self.root_dir
        )

        backup_path = (
            self.backup_dir
            / timestamp
            / relative
        )

        backup_path.parent.mkdir(
            exist_ok=True,
            parents=True
        )

        shutil.copy2(
            target,
            backup_path
        )

        return backup_path

    # =========================================
    # SYNTAX CHECK
    # =========================================

    def _check_syntax(self, target):

        try:
            code = target.read_text(
                encoding="utf-8"
            )

            compile(
                code,
                str(target),
                "exec"
            )

            return True, "Syntax OK"

        except Exception as e:
            return False, str(e)

    # =========================================
    # RESTORE BACKUP
    # =========================================

    def _restore_backup(
        self,
        backup_path,
        target
    ):

        try:
            shutil.copy2(
                backup_path,
                target
            )

            return True

        except Exception as e:

            print(
                f"[AZAD ERROR] Rollback failed: {e}"
            )

            return False

    # =========================================
    # MODIFY CODE
    # =========================================

    def modify_code(
        self,
        file_path,
        new_code
    ):

        target = Path(
            file_path
        ).resolve()

        print(
            "[AZAD EVOLUTION] "
            "Starting controlled self-modification..."
        )

        # -------------------------------------
        # SECURITY
        # -------------------------------------

        if not self._is_safe_target(
            file_path
        ):

            return {
                "success": False,
                "changed": False,
                "message": (
                    "Modification target is "
                    "protected or outside AZAD."
                )
            }

        # -------------------------------------
        # FILE CHECK
        # -------------------------------------

        if not target.exists():

            return {
                "success": False,
                "changed": False,
                "message": "File does not exist."
            }

        if not target.is_file():

            return {
                "success": False,
                "changed": False,
                "message": "Target is not a file."
            }

        # -------------------------------------
        # READ OLD CODE
        # -------------------------------------

        try:

            old_code = target.read_text(
                encoding="utf-8"
            )

        except Exception as e:

            return {
                "success": False,
                "changed": False,
                "message": (
                    f"Could not read file: {e}"
                )
            }

        # -------------------------------------
        # NO CHANGE
        # -------------------------------------

        if old_code == new_code:

            return {
                "success": True,
                "changed": False,
                "message": (
                    "Code is already identical."
                )
            }

        # -------------------------------------
        # BACKUP
        # -------------------------------------

        try:

            backup_path = self._create_backup(
                target
            )

        except Exception as e:

            return {
                "success": False,
                "changed": False,
                "message": (
                    f"Backup failed: {e}"
                )
            }

        print(
            f"[AZAD EVOLUTION] Backup created: "
            f"{backup_path}"
        )

        # -------------------------------------
        # WRITE
        # -------------------------------------

        try:

            target.write_text(
                new_code,
                encoding="utf-8"
            )

        except Exception as e:

            self._restore_backup(
                backup_path,
                target
            )

            return {
                "success": False,
                "changed": False,
                "message": (
                    f"Write failed: {e}"
                ),
                "backup": str(
                    backup_path
                )
            }

        # -------------------------------------
        # SYNTAX TEST
        # -------------------------------------

        syntax_ok, syntax_message = (
            self._check_syntax(target)
        )

        if not syntax_ok:

            print(
                "[AZAD EVOLUTION] "
                "Syntax check failed."
            )

            rollback_ok = self._restore_backup(
                backup_path,
                target
            )

            return {
                "success": False,
                "changed": False,
                "message": (
                    "Syntax check failed. "
                    "Previous version restored."
                ),
                "error": syntax_message,
                "backup": str(
                    backup_path
                ),
                "rollback": rollback_ok
            }

        # -------------------------------------
        # SUCCESS
        # -------------------------------------

        print(
            "[AZAD EVOLUTION] "
            "Self-modification successful."
        )

        return {
            "success": True,
            "changed": True,
            "message": (
                "Code successfully modified "
                "and syntax validated."
            ),
            "file": str(target),
            "backup": str(
                backup_path
            )
        }

    # =========================================
    # PUBLIC ROLLBACK
    # =========================================

    def rollback(
        self,
        backup_path,
        file_path
    ):

        target = Path(
            file_path
        ).resolve()

        backup = Path(
            backup_path
        ).resolve()

        if not backup.exists():

            return {
                "success": False,
                "message": "Backup does not exist."
            }

        if not target.exists():

            return {
                "success": False,
                "message": "Target file does not exist."
            }

        success = self._restore_backup(
            backup,
            target
        )

        if success:

            return {
                "success": True,
                "message": (
                    "Previous version restored."
                )
            }

        return {
            "success": False,
            "message": "Rollback failed."
        }