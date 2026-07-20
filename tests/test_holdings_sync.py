import os

from models.account import PortfolioAccount
from models.stored_holding import StoredHolding

from services.portfolio_database import PortfolioDatabase
from services.holdings_database import HoldingsDatabase
from services.holdings_sync_service import HoldingsSyncService


TEST_DATABASE = (
    r"D:\PMPH\data\test_holdings_sync.db"
)


def make_holding(
    account_id,
    symbol,
    isin,
    quantity,
    average_price,
    current_price,
    source_file,
):

    invested_value = (
        quantity
        * average_price
    )

    current_value = (
        quantity
        * current_price
    )

    profit_loss = (
        current_value
        - invested_value
    )

    if invested_value:

        profit_loss_percent = (
            profit_loss
            / invested_value
            * 100
        )

    else:

        profit_loss_percent = 0.0

    return StoredHolding(
        account_id=account_id,
        symbol=symbol,
        name=f"{symbol} Holding",
        isin=isin,
        asset_type="ETF",
        quantity=quantity,
        average_price=average_price,
        current_price=current_price,
        invested_value=invested_value,
        current_value=current_value,
        profit_loss=profit_loss,
        profit_loss_percent=profit_loss_percent,
        source_file=source_file,
    )


def main():

    print("=" * 74)
    print("PMPH FULL STATEMENT SYNCHRONIZATION TEST")
    print("=" * 74)

    if os.path.exists(
        TEST_DATABASE
    ):

        os.remove(
            TEST_DATABASE
        )

    portfolio_database = (
        PortfolioDatabase(
            TEST_DATABASE
        )
    )

    account = (
        portfolio_database.save_account(
            PortfolioAccount(
                owner_name="Test Owner",
                platform_name="Test Broker",
                account_name="Main Account",
            )
        )
    )

    holdings_database = (
        HoldingsDatabase(
            TEST_DATABASE
        )
    )

    sync_service = (
        HoldingsSyncService(
            holdings_database
        )
    )

    # =====================================================
    # INITIAL FULL STATEMENT
    # =====================================================

    initial_statement = [

        make_holding(
            account.account_id,
            "MIDCAP",
            "TESTISIN001",
            100,
            20,
            22,
            "statement_1.xlsx",
        ),

        make_holding(
            account.account_id,
            "SMALLCAP",
            "TESTISIN002",
            200,
            40,
            44,
            "statement_1.xlsx",
        ),

        make_holding(
            account.account_id,
            "GOLDBEES",
            "TESTISIN003",
            50,
            100,
            110,
            "statement_1.xlsx",
        ),
    ]

    result_1 = (
        sync_service.synchronize(
            account_id=account.account_id,
            incoming_holdings=initial_statement,
            mode=HoldingsSyncService.FULL,
        )
    )

    print()
    print("INITIAL FULL STATEMENT")
    print("-" * 74)

    print(
        "Success:",
        result_1.success
    )

    print(
        "Added:",
        result_1.added_count
    )

    print(
        "Updated:",
        result_1.updated_count
    )

    print(
        "Removed:",
        result_1.removed_count
    )

    print(
        "Holdings Stored:",
        holdings_database.count_holdings(
            account.account_id
        )
    )

    # =====================================================
    # PARTIAL IMPORT
    #
    # Only MIDCAP appears.
    # SMALLCAP and GOLDBEES MUST NOT be removed.
    # =====================================================

    partial_statement = [

        make_holding(
            account.account_id,
            "MIDCAP",
            "TESTISIN001",
            110,
            20.50,
            23,
            "partial_update.xlsx",
        ),
    ]

    result_2 = (
        sync_service.synchronize(
            account_id=account.account_id,
            incoming_holdings=partial_statement,
            mode=HoldingsSyncService.PARTIAL,
        )
    )

    print()
    print("PARTIAL IMPORT")
    print("-" * 74)

    print(
        "Success:",
        result_2.success
    )

    print(
        "Updated:",
        result_2.updated_count
    )

    print(
        "Removed:",
        result_2.removed_count
    )

    print(
        "Holdings Stored:",
        holdings_database.count_holdings(
            account.account_id
        )
    )

    # =====================================================
    # NEW FULL STATEMENT
    #
    # GOLDBEES has disappeared because it was sold.
    # MIDCAP changes.
    # SMALLCAP remains.
    # NEWETF is added.
    # =====================================================

    latest_full_statement = [

        make_holding(
            account.account_id,
            "MIDCAP",
            "TESTISIN001",
            125,
            20.75,
            24,
            "statement_2.xlsx",
        ),

        make_holding(
            account.account_id,
            "SMALLCAP",
            "TESTISIN002",
            220,
            41,
            46,
            "statement_2.xlsx",
        ),

        make_holding(
            account.account_id,
            "NEWETF",
            "TESTISIN004",
            75,
            50,
            55,
            "statement_2.xlsx",
        ),
    ]

    result_3 = (
        sync_service.synchronize(
            account_id=account.account_id,
            incoming_holdings=latest_full_statement,
            mode=HoldingsSyncService.FULL,
        )
    )

    print()
    print("LATEST FULL STATEMENT")
    print("-" * 74)

    print(
        "Success:",
        result_3.success
    )

    print(
        "Added:",
        result_3.added_count
    )

    print(
        "Updated:",
        result_3.updated_count
    )

    print(
        "Removed:",
        result_3.removed_count
    )

    print(
        "Holdings Stored:",
        holdings_database.count_holdings(
            account.account_id
        )
    )

    # =====================================================
    # FINAL HOLDINGS
    # =====================================================

    final_holdings = (
        holdings_database.list_holdings(
            account.account_id
        )
    )

    final_symbols = {
        holding.symbol
        for holding
        in final_holdings
    }

    print()
    print("FINAL CURRENT HOLDINGS")
    print("-" * 74)

    for holding in final_holdings:

        print(
            holding.symbol,
            "->",
            holding.quantity
        )

    print()
    print("-" * 74)

    partial_safe = (
        result_2.removed_count == 0
        and holdings_database is not None
    )

    sold_removed = (
        "GOLDBEES"
        not in final_symbols
    )

    expected_final = (
        final_symbols
        == {
            "MIDCAP",
            "SMALLCAP",
            "NEWETF",
        }
    )

    print(
        "Partial Import Removal Protection:",
        (
            "PASS"
            if partial_safe
            else "FAIL"
        )
    )

    print(
        "Sold Security Removed On Full Sync:",
        (
            "PASS"
            if sold_removed
            else "FAIL"
        )
    )

    print(
        "Final Portfolio Matches Latest Statement:",
        (
            "PASS"
            if expected_final
            else "FAIL"
        )
    )

    print(
        "Final Holding Count:",
        (
            "PASS"
            if len(
                final_holdings
            ) == 3
            else "FAIL"
        )
    )

    print()
    print("=" * 74)
    print("SYNCHRONIZATION TEST COMPLETE")
    print("=" * 74)


if __name__ == "__main__":

    main()