import os
from pathlib import Path
from types import SimpleNamespace

from models.account import PortfolioAccount

from services.portfolio_database import (
    PortfolioDatabase,
)

from services.portfolio_import_service import (
    PortfolioImportService,
)

from services.portfolio_batch_import_service import (
    PortfolioBatchImportService,
    BatchImportItem,
)


TEST_DATABASE = Path(
    r"D:\PMPH\data\test_batch_import.db"
)

TEST_BACKUPS = Path(
    r"D:\PMPH\data\test_batch_backups"
)


class ValidationResult:
    """
    Minimal test-only object matching the interface
    expected by PortfolioImportService.
    """

    def __init__(
        self,
        holding,
        is_valid=True,
    ):

        self.holding = holding
        self.is_valid = is_valid


class ForcedBackupFailure:
    """
    Simulates backup failure.

    Used to prove that a failed backup prevents
    every database write in the batch.
    """

    class Result:
        success = False
        backup_path = ""
        error = (
            "Forced backup failure for test."
        )

    def create_backup(
        self,
        reason="before_import",
    ):

        return self.Result()


def make_validation(
    symbol,
    isin,
    quantity,
):

    price = 100.0

    # Test-only universal holding representation.
    #
    # PortfolioImportService only requires these
    # attributes from validation_result.holding.

    holding = SimpleNamespace(
        broker="Auto-Detected",

        asset_type="ETF",

        symbol=symbol,

        name=symbol,

        isin=isin,

        quantity=float(
            quantity
        ),

        average_price=price,

        current_price=price,

        invested_value=(
            float(
                quantity
            )
            * price
        ),

        current_value=(
            float(
                quantity
            )
            * price
        ),

        profit_loss=0.0,

        profit_loss_percent=0.0,
    )

    return ValidationResult(
        holding=holding,
        is_valid=True,
    )


def remove_test_database():

    if TEST_DATABASE.exists():

        TEST_DATABASE.unlink()


def main():

    print("=" * 76)

    print(
        "PMPH PROTECTED BATCH IMPORT TEST"
    )

    print("=" * 76)

    # =====================================================
    # CLEAN TEST DATABASE
    # =====================================================

    remove_test_database()

    TEST_BACKUPS.mkdir(
        parents=True,
        exist_ok=True,
    )

    # =====================================================
    # CREATE TWO TEST ACCOUNTS
    # =====================================================

    portfolio_database = (
        PortfolioDatabase(
            str(
                TEST_DATABASE
            )
        )
    )

    account_one = (
        portfolio_database.save_account(
            PortfolioAccount(
                owner_name="Jaideep",

                platform_name=(
                    "ProStocks"
                ),

                account_name="Jaideep",
            )
        )
    )

    account_two = (
        portfolio_database.save_account(
            PortfolioAccount(
                owner_name="Anita",

                platform_name=(
                    "Zerodha"
                ),

                account_name="Anita",
            )
        )
    )

    import_service = (
        PortfolioImportService(
            str(
                TEST_DATABASE
            )
        )
    )

    # =====================================================
    # TEST 1:
    # FORCED BACKUP FAILURE MUST BLOCK ALL WRITES
    # =====================================================

    failure_batch_service = (
        PortfolioBatchImportService(
            portfolio_import_service=(
                import_service
            ),

            database_path=str(
                TEST_DATABASE
            ),

            backup_directory=str(
                TEST_BACKUPS
            ),

            backup_service=(
                ForcedBackupFailure()
            ),
        )
    )

    failure_items = [
        BatchImportItem(
            source_file=(
                "prostocks.xlsx"
            ),

            account=account_one,

            validation_results=[
                make_validation(
                    "GOLDBEES",

                    "TESTGOLD001",

                    496,
                )
            ],

            mode="FULL",
        )
    ]

    before_failure_count = len(
        import_service
        .get_all_holdings()
    )

    failure_result = (
        failure_batch_service
        .import_batch(
            failure_items
        )
    )

    after_failure_count = len(
        import_service
        .get_all_holdings()
    )

    print()

    print(
        "FORCED BACKUP FAILURE"
    )

    print("-" * 76)

    print(
        "Batch Success:",
        failure_result.success,
    )

    print(
        "Backup Created:",
        failure_result.backup_created,
    )

    print(
        "Holdings Before:",
        before_failure_count,
    )

    print(
        "Holdings After:",
        after_failure_count,
    )

    if failure_result.errors:

        print(
            "Errors:"
        )

        for error in (
            failure_result.errors
        ):

            print(
                "-",
                error,
            )

    # =====================================================
    # TEST 2:
    # VERIFIED BACKUP + TWO-FILE REAL BATCH
    # =====================================================

    batch_service = (
        PortfolioBatchImportService(
            portfolio_import_service=(
                import_service
            ),

            database_path=str(
                TEST_DATABASE
            ),

            backup_directory=str(
                TEST_BACKUPS
            ),
        )
    )

    items = [
        BatchImportItem(
            source_file=(
                "prostocks.xlsx"
            ),

            account=account_one,

            validation_results=[
                make_validation(
                    "GOLDBEES",

                    "TESTGOLD001",

                    496,
                )
            ],

            mode="FULL",
        ),

        BatchImportItem(
            source_file=(
                "zerodha.xlsx"
            ),

            account=account_two,

            validation_results=[
                make_validation(
                    "HDFCSML250",

                    "TESTSMALL001",

                    131,
                ),

                make_validation(
                    "MIDCAP",

                    "TESTMID001",

                    8254,
                ),

                make_validation(
                    "SMALLCAP",

                    "TESTSMALL002",

                    5683,
                ),
            ],

            mode="FULL",
        ),
    ]

    result = (
        batch_service.import_batch(
            items
        )
    )

    holdings = (
        import_service
        .get_all_holdings()
    )

    print()

    print(
        "PROTECTED TWO-FILE IMPORT"
    )

    print("-" * 76)

    print(
        "Batch Success:",
        result.success,
    )

    print(
        "Backup Created:",
        result.backup_created,
    )

    print(
        "Backup Path:",
        result.backup_path,
    )

    print(
        "Total Files:",
        result.total_files,
    )

    print(
        "Completed Files:",
        result.completed_files,
    )

    print(
        "Final Holdings:",
        len(
            holdings
        ),
    )

    if result.errors:

        print(
            "Errors:"
        )

        for error in (
            result.errors
        ):

            print(
                "-",
                error,
            )

    print()

    for holding in holdings:

        print(
            holding.symbol,
            "->",
            holding.quantity,
        )

    # =====================================================
    # FINAL ASSERTION-STYLE CHECKS
    # =====================================================

    print()

    print("-" * 76)

    backup_failure_pass = (
        not failure_result.success
        and not (
            failure_result
            .backup_created
        )
        and before_failure_count
        == after_failure_count
        == 0
    )

    verified_backup_pass = (
        result.backup_created
        and bool(
            result.backup_path
        )
        and os.path.exists(
            result.backup_path
        )
    )

    two_file_batch_pass = (
        result.success
        and result.total_files
        == 2
        and result.completed_files
        == 2
    )

    expected_holdings_pass = (
        len(
            holdings
        )
        == 4
    )

    expected_symbols = {
        holding.symbol
        for holding
        in holdings
    }

    symbols_pass = (
        expected_symbols
        == {
            "GOLDBEES",
            "HDFCSML250",
            "MIDCAP",
            "SMALLCAP",
        }
    )

    print(
        "Backup Failure Blocks Writes:",
        (
            "PASS"
            if backup_failure_pass
            else "FAIL"
        ),
    )

    print(
        "Verified Backup Created:",
        (
            "PASS"
            if verified_backup_pass
            else "FAIL"
        ),
    )

    print(
        "Two-File Batch Completed:",
        (
            "PASS"
            if two_file_batch_pass
            else "FAIL"
        ),
    )

    print(
        "Expected Holdings Imported:",
        (
            "PASS"
            if expected_holdings_pass
            else "FAIL"
        ),
    )

    print(
        "Expected Securities Match:",
        (
            "PASS"
            if symbols_pass
            else "FAIL"
        ),
    )

    print()

    print("=" * 76)

    print(
        "PROTECTED BATCH IMPORT TEST COMPLETE"
    )

    print("=" * 76)


if __name__ == "__main__":

    main()