from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import shutil
import sqlite3


@dataclass
class DatabaseBackupResult:
    success: bool
    source_path: str = ""
    backup_path: str = ""
    source_size: int = 0
    backup_size: int = 0
    integrity_check: str = ""
    error: str = ""


class DatabaseBackupService:
    """
    Creates and verifies safety backups of the PMPH SQLite database.

    Safety rules:

    - Never modifies the source database.
    - Creates a timestamped backup before protected operations.
    - Verifies that the backup file exists.
    - Verifies that the backup is non-empty.
    - Runs SQLite PRAGMA integrity_check on the backup.
    - Reports failure if any verification step fails.
    """

    def __init__(
        self,
        database_path="data/pmph_portfolio.db",
        backup_directory="data/backups",
    ):

        self.database_path = Path(
            database_path
        )

        self.backup_directory = Path(
            backup_directory
        )

    # =====================================================
    # CREATE VERIFIED BACKUP
    # =====================================================

    def create_backup(
        self,
        reason="before_import",
    ):

        source_path = (
            self.database_path
        )

        if not source_path.exists():

            return DatabaseBackupResult(
                success=False,
                source_path=str(
                    source_path
                ),
                error=(
                    "Source database does not exist."
                ),
            )

        try:

            source_size = (
                source_path.stat().st_size
            )

        except OSError as error:

            return DatabaseBackupResult(
                success=False,
                source_path=str(
                    source_path
                ),
                error=(
                    "Could not inspect source database: "
                    f"{error}"
                ),
            )

        if source_size <= 0:

            return DatabaseBackupResult(
                success=False,
                source_path=str(
                    source_path
                ),
                source_size=(
                    source_size
                ),
                error=(
                    "Source database is empty."
                ),
            )

        try:

            self.backup_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

        except OSError as error:

            return DatabaseBackupResult(
                success=False,
                source_path=str(
                    source_path
                ),
                source_size=(
                    source_size
                ),
                error=(
                    "Could not create backup directory: "
                    f"{error}"
                ),
            )

        safe_reason = self._safe_name(
            reason
        )

        timestamp = (
            datetime.now().strftime(
                "%Y%m%d_%H%M%S_%f"
            )
        )

        backup_name = (
            f"{source_path.stem}_"
            f"{safe_reason}_"
            f"{timestamp}"
            f"{source_path.suffix or '.db'}"
        )

        backup_path = (
            self.backup_directory
            / backup_name
        )

        try:

            # ---------------------------------------------
            # Use SQLite's own backup API.
            #
            # This is safer than a plain file copy when
            # the source database may be open/in use.
            # ---------------------------------------------

            source_connection = (
                sqlite3.connect(
                    str(
                        source_path
                    )
                )
            )

            try:

                backup_connection = (
                    sqlite3.connect(
                        str(
                            backup_path
                        )
                    )
                )

                try:

                    source_connection.backup(
                        backup_connection
                    )

                    backup_connection.commit()

                finally:

                    backup_connection.close()

            finally:

                source_connection.close()

        except Exception as error:

            self._remove_failed_backup(
                backup_path
            )

            return DatabaseBackupResult(
                success=False,
                source_path=str(
                    source_path
                ),
                backup_path=str(
                    backup_path
                ),
                source_size=(
                    source_size
                ),
                error=(
                    "Database backup failed: "
                    f"{error}"
                ),
            )

        # =================================================
        # VERIFY BACKUP FILE
        # =================================================

        if not backup_path.exists():

            return DatabaseBackupResult(
                success=False,
                source_path=str(
                    source_path
                ),
                backup_path=str(
                    backup_path
                ),
                source_size=(
                    source_size
                ),
                error=(
                    "Backup file was not created."
                ),
            )

        try:

            backup_size = (
                backup_path.stat().st_size
            )

        except OSError as error:

            return DatabaseBackupResult(
                success=False,
                source_path=str(
                    source_path
                ),
                backup_path=str(
                    backup_path
                ),
                source_size=(
                    source_size
                ),
                error=(
                    "Could not inspect backup file: "
                    f"{error}"
                ),
            )

        if backup_size <= 0:

            self._remove_failed_backup(
                backup_path
            )

            return DatabaseBackupResult(
                success=False,
                source_path=str(
                    source_path
                ),
                backup_path=str(
                    backup_path
                ),
                source_size=(
                    source_size
                ),
                backup_size=(
                    backup_size
                ),
                error=(
                    "Backup file is empty."
                ),
            )

        # =================================================
        # SQLITE INTEGRITY CHECK
        # =================================================

        try:

            integrity_check = (
                self._integrity_check(
                    backup_path
                )
            )

        except Exception as error:

            self._remove_failed_backup(
                backup_path
            )

            return DatabaseBackupResult(
                success=False,
                source_path=str(
                    source_path
                ),
                backup_path=str(
                    backup_path
                ),
                source_size=(
                    source_size
                ),
                backup_size=(
                    backup_size
                ),
                error=(
                    "Backup integrity verification failed: "
                    f"{error}"
                ),
            )

        if (
            integrity_check
            .strip()
            .lower()
            != "ok"
        ):

            self._remove_failed_backup(
                backup_path
            )

            return DatabaseBackupResult(
                success=False,
                source_path=str(
                    source_path
                ),
                backup_path=str(
                    backup_path
                ),
                source_size=(
                    source_size
                ),
                backup_size=(
                    backup_size
                ),
                integrity_check=(
                    integrity_check
                ),
                error=(
                    "SQLite integrity check did not "
                    "return OK."
                ),
            )

        return DatabaseBackupResult(
            success=True,
            source_path=str(
                source_path
            ),
            backup_path=str(
                backup_path
            ),
            source_size=(
                source_size
            ),
            backup_size=(
                backup_size
            ),
            integrity_check=(
                integrity_check
            ),
        )

    # =====================================================
    # VERIFY EXISTING DATABASE
    # =====================================================

    def verify_database(
        self,
        database_path=None,
    ):

        path = Path(
            database_path
            or self.database_path
        )

        if not path.exists():

            return False, (
                "Database does not exist."
            )

        if path.stat().st_size <= 0:

            return False, (
                "Database is empty."
            )

        try:

            result = (
                self._integrity_check(
                    path
                )
            )

        except Exception as error:

            return False, str(
                error
            )

        if (
            result.strip().lower()
            == "ok"
        ):

            return True, "ok"

        return False, result

    # =====================================================
    # RESTORE BACKUP
    # =====================================================

    def restore_backup(
        self,
        backup_path,
        destination_path=None,
    ):

        """
        Restore a verified backup.

        This method is intentionally separate from normal
        import flow. PMPH should never restore automatically.
        """

        backup_path = Path(
            backup_path
        )

        destination_path = Path(
            destination_path
            or self.database_path
        )

        valid, message = (
            self.verify_database(
                backup_path
            )
        )

        if not valid:

            raise ValueError(
                "Backup cannot be restored: "
                f"{message}"
            )

        destination_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            backup_path,
            destination_path,
        )

        valid, message = (
            self.verify_database(
                destination_path
            )
        )

        if not valid:

            raise RuntimeError(
                "Restored database failed "
                "integrity verification: "
                f"{message}"
            )

        return str(
            destination_path
        )

    # =====================================================
    # INTERNAL HELPERS
    # =====================================================

    @staticmethod
    def _integrity_check(
        database_path,
    ):

        connection = sqlite3.connect(
            str(
                database_path
            )
        )

        try:

            row = connection.execute(
                "PRAGMA integrity_check"
            ).fetchone()

        finally:

            connection.close()

        if not row:

            return ""

        return str(
            row[0]
        )

    @staticmethod
    def _safe_name(
        value,
    ):

        value = (
            str(
                value
                or "backup"
            )
            .strip()
            .lower()
        )

        cleaned = []

        for character in value:

            if (
                character.isalnum()
                or character
                in {
                    "_",
                    "-",
                }
            ):

                cleaned.append(
                    character
                )

            else:

                cleaned.append(
                    "_"
                )

        result = "".join(
            cleaned
        ).strip(
            "_"
        )

        return (
            result
            or "backup"
        )

    @staticmethod
    def _remove_failed_backup(
        backup_path,
    ):

        try:

            if backup_path.exists():

                backup_path.unlink()

        except OSError:

            pass