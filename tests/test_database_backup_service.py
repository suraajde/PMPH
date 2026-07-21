import os
import sqlite3
from pathlib import Path

from services.database_backup_service import (
    DatabaseBackupService,
)


TEST_DIRECTORY = Path(
    r"D:\PMPH\data\backup_test"
)

TEST_DATABASE = (
    TEST_DIRECTORY
    / "test_portfolio.db"
)

TEST_BACKUP_DIRECTORY = (
    TEST_DIRECTORY
    / "backups"
)

RESTORED_DATABASE = (
    TEST_DIRECTORY
    / "restored_portfolio.db"
)


def remove_file(
    path,
):

    if path.exists():

        path.unlink()


def main():

    print("=" * 76)
    print("PMPH DATABASE BACKUP SAFETY TEST")
    print("=" * 76)

    TEST_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    remove_file(
        TEST_DATABASE
    )

    remove_file(
        RESTORED_DATABASE
    )

    # =====================================================
    # CREATE TEST DATABASE
    # =====================================================

    connection = sqlite3.connect(
        str(
            TEST_DATABASE
        )
    )

    try:

        connection.execute(
            """
            CREATE TABLE holdings (
                id INTEGER PRIMARY KEY,
                symbol TEXT NOT NULL,
                quantity REAL NOT NULL
            )
            """
        )

        connection.execute(
            """
            INSERT INTO holdings (
                symbol,
                quantity
            )
            VALUES (?, ?)
            """,
            (
                "MIDCAP",
                125.0,
            ),
        )

        connection.execute(
            """
            INSERT INTO holdings (
                symbol,
                quantity
            )
            VALUES (?, ?)
            """,
            (
                "SMALLCAP",
                220.0,
            ),
        )

        connection.commit()

    finally:

        connection.close()

    print()
    print(
        "Test Database Created:",
        TEST_DATABASE.exists(),
    )

    # =====================================================
    # CREATE BACKUP
    # =====================================================

    service = DatabaseBackupService(
        database_path=(
            str(
                TEST_DATABASE
            )
        ),

        backup_directory=(
            str(
                TEST_BACKUP_DIRECTORY
            )
        ),
    )

    backup_result = (
        service.create_backup(
            reason="before_import"
        )
    )

    print()
    print("BACKUP RESULT")
    print("-" * 76)

    print(
        "Success:",
        backup_result.success,
    )

    print(
        "Source:",
        backup_result.source_path,
    )

    print(
        "Backup:",
        backup_result.backup_path,
    )

    print(
        "Source Size:",
        backup_result.source_size,
    )

    print(
        "Backup Size:",
        backup_result.backup_size,
    )

    print(
        "Integrity:",
        backup_result.integrity_check,
    )

    if backup_result.error:

        print(
            "Error:",
            backup_result.error,
        )

    # =====================================================
    # VERIFY BACKUP CONTENT
    # =====================================================

    backup_row_count = 0

    if backup_result.success:

        backup_connection = (
            sqlite3.connect(
                backup_result.backup_path
            )
        )

        try:

            backup_row_count = (
                backup_connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM holdings
                    """
                ).fetchone()[0]
            )

        finally:

            backup_connection.close()

    print()
    print(
        "Rows In Backup:",
        backup_row_count,
    )

    # =====================================================
    # SIMULATE SOURCE DATABASE CHANGE
    # =====================================================

    connection = sqlite3.connect(
        str(
            TEST_DATABASE
        )
    )

    try:

        connection.execute(
            """
            DELETE FROM holdings
            WHERE symbol = ?
            """,
            (
                "MIDCAP",
            ),
        )

        connection.commit()

    finally:

        connection.close()

    # =====================================================
    # RESTORE BACKUP TO SEPARATE DATABASE
    # =====================================================

    restored_path = (
        service.restore_backup(
            backup_path=(
                backup_result.backup_path
            ),

            destination_path=(
                str(
                    RESTORED_DATABASE
                )
            ),
        )
        if backup_result.success
        else ""
    )

    restored_row_count = 0

    if restored_path:

        restored_connection = (
            sqlite3.connect(
                restored_path
            )
        )

        try:

            restored_row_count = (
                restored_connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM holdings
                    """
                ).fetchone()[0]
            )

        finally:

            restored_connection.close()

    print()
    print("RESTORE TEST")
    print("-" * 76)

    print(
        "Restored Database:",
        restored_path,
    )

    print(
        "Rows After Restore:",
        restored_row_count,
    )

    # =====================================================
    # FINAL CHECKS
    # =====================================================

    print()
    print("-" * 76)

    print(
        "Backup Creation:",
        (
            "PASS"
            if backup_result.success
            else "FAIL"
        ),
    )

    print(
        "Backup Integrity:",
        (
            "PASS"
            if (
                backup_result.integrity_check
                .strip()
                .lower()
                == "ok"
            )
            else "FAIL"
        ),
    )

    print(
        "Backup Data Preserved:",
        (
            "PASS"
            if backup_row_count
            == 2
            else "FAIL"
        ),
    )

    print(
        "Restore Data Preserved:",
        (
            "PASS"
            if restored_row_count
            == 2
            else "FAIL"
        ),
    )

    print()
    print("=" * 76)
    print("DATABASE BACKUP SAFETY TEST COMPLETE")
    print("=" * 76)


if __name__ == "__main__":
    main()