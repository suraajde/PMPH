from dataclasses import dataclass, field
from typing import List

from services.database_backup_service import (
    DatabaseBackupService,
)


@dataclass
class BatchImportItem:
    """
    One confirmed file/import operation inside a batch.
    """

    source_file: str

    account: object

    validation_results: list

    mode: str


@dataclass
class BatchImportResult:
    """
    Result of one protected multi-file import batch.
    """

    success: bool

    backup_created: bool = False

    backup_path: str = ""

    total_files: int = 0

    completed_files: int = 0

    import_results: List = field(
        default_factory=list
    )

    errors: List[str] = field(
        default_factory=list
    )


class PortfolioBatchImportService:
    """
    Coordinates a protected multi-file PMPH import.

    Safety sequence:

    1. Validate the entire batch.
    2. Reject unsafe duplicate FULL assignments.
    3. Preview every item.
    4. Create ONE verified pre-import database backup.
    5. Only after backup success, begin database writes.
    6. Return individual import results and backup path.

    This service does NOT automatically restore a backup.
    """

    FULL = "FULL"
    PARTIAL = "PARTIAL"

    def __init__(
        self,
        portfolio_import_service,
        database_path="data/pmph_portfolio.db",
        backup_directory="data/backups",
        backup_service=None,
    ):

        self.portfolio_import_service = (
            portfolio_import_service
        )

        if backup_service is None:

            backup_service = (
                DatabaseBackupService(
                    database_path=database_path,
                    backup_directory=(
                        backup_directory
                    ),
                )
            )

        self.backup_service = (
            backup_service
        )

    # =====================================================
    # PUBLIC BATCH IMPORT
    # =====================================================

    def import_batch(
        self,
        items,
    ):

        items = list(
            items
            or []
        )

        if not items:

            return BatchImportResult(
                success=False,
                errors=[
                    "No import items were supplied."
                ],
            )

        # -------------------------------------------------
        # Validate complete batch before any backup/write.
        # -------------------------------------------------

        validation_errors = (
            self._validate_batch(
                items
            )
        )

        if validation_errors:

            return BatchImportResult(
                success=False,
                total_files=len(
                    items
                ),
                errors=(
                    validation_errors
                ),
            )

        # -------------------------------------------------
        # Run read-only previews again immediately before
        # backup/import.
        #
        # This ensures the batch is still interpretable by
        # exactly the same conversion logic used for import.
        # -------------------------------------------------

        preview_errors = []

        for item in items:

            preview = (
                self.portfolio_import_service
                .preview_validated_holdings(
                    account=(
                        item.account
                    ),

                    validation_results=(
                        item.validation_results
                    ),

                    mode=(
                        item.mode
                    ),

                    source_file=(
                        item.source_file
                    ),
                )
            )

            if not preview.success:

                if preview.errors:

                    for error in (
                        preview.errors
                    ):

                        preview_errors.append(
                            (
                                f"{item.source_file}: "
                                f"{error}"
                            )
                        )

                else:

                    preview_errors.append(
                        (
                            f"{item.source_file}: "
                            "pre-import preview failed."
                        )
                    )

        if preview_errors:

            return BatchImportResult(
                success=False,
                total_files=len(
                    items
                ),
                errors=(
                    preview_errors
                ),
            )

        # -------------------------------------------------
        # Create ONE verified backup before first write.
        # -------------------------------------------------

        backup_result = (
            self.backup_service
            .create_backup(
                reason="before_import"
            )
        )

        if not backup_result.success:

            return BatchImportResult(
                success=False,

                backup_created=False,

                backup_path=(
                    backup_result
                    .backup_path
                ),

                total_files=len(
                    items
                ),

                completed_files=0,

                errors=[
                    (
                        "Import blocked because the "
                        "pre-import database backup failed: "
                        f"{backup_result.error}"
                    )
                ],
            )

        # -------------------------------------------------
        # Backup exists and passed integrity verification.
        # Database writes may now begin.
        # -------------------------------------------------

        import_results = []

        completed_files = 0

        batch_errors = []

        for item in items:

            result = (
                self.portfolio_import_service
                .import_validated_holdings(
                    account=(
                        item.account
                    ),

                    validation_results=(
                        item.validation_results
                    ),

                    mode=(
                        item.mode
                    ),

                    source_file=(
                        item.source_file
                    ),
                )
            )

            import_results.append(
                result
            )

            completed_files += 1

            if not result.success:

                if result.errors:

                    for error in (
                        result.errors
                    ):

                        batch_errors.append(
                            (
                                f"{item.source_file}: "
                                f"{error}"
                            )
                        )

                else:

                    batch_errors.append(
                        (
                            f"{item.source_file}: "
                            "import failed."
                        )
                    )

                # -----------------------------------------
                # Stop the batch after the first failed
                # import.
                #
                # Do NOT automatically restore.
                # The verified pre-import backup remains
                # available for explicit recovery.
                # -----------------------------------------

                break

        success = (
            completed_files
            == len(
                items
            )
            and all(
                result.success
                for result
                in import_results
            )
            and not batch_errors
        )

        return BatchImportResult(
            success=success,

            backup_created=True,

            backup_path=(
                backup_result
                .backup_path
            ),

            total_files=len(
                items
            ),

            completed_files=(
                completed_files
            ),

            import_results=(
                import_results
            ),

            errors=(
                batch_errors
            ),
        )

    # =====================================================
    # COMPLETE BATCH VALIDATION
    # =====================================================

    def _validate_batch(
        self,
        items,
    ):

        errors = []

        full_files_by_account = {}

        for index, item in enumerate(
            items,
            start=1,
        ):

            source_file = str(
                item.source_file
                or ""
            ).strip()

            if not source_file:

                errors.append(
                    (
                        f"Import item {index} "
                        "has no source file name."
                    )
                )

            if item.account is None:

                errors.append(
                    (
                        f"{source_file or index}: "
                        "no portfolio account assigned."
                    )
                )

                continue

            account_id = str(
                getattr(
                    item.account,
                    "account_id",
                    "",
                )
                or ""
            ).strip()

            if not account_id:

                errors.append(
                    (
                        f"{source_file or index}: "
                        "assigned account has no account ID."
                    )
                )

                continue

            mode = str(
                item.mode
                or ""
            ).strip().upper()

            if mode not in {
                self.FULL,
                self.PARTIAL,
            }:

                errors.append(
                    (
                        f"{source_file or index}: "
                        "import mode must be "
                        "FULL or PARTIAL."
                    )
                )

                continue

            if not item.validation_results:

                errors.append(
                    (
                        f"{source_file or index}: "
                        "no validation results supplied."
                    )
                )

            if mode == self.FULL:

                if (
                    account_id
                    not in full_files_by_account
                ):

                    full_files_by_account[
                        account_id
                    ] = []

                full_files_by_account[
                    account_id
                ].append(
                    source_file
                    or f"Item {index}"
                )

        # -------------------------------------------------
        # Never allow two FULL files for the same account
        # in one batch.
        # -------------------------------------------------

        for (
            account_id,
            source_files,
        ) in (
            full_files_by_account.items()
        ):

            if len(
                source_files
            ) <= 1:

                continue

            errors.append(
                (
                    "Unsafe batch: multiple FULL "
                    "statements are assigned to account "
                    f"{account_id}: "
                    + ", ".join(
                        source_files
                    )
                )
            )

        return errors