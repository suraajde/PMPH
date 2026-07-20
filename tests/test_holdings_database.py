import os

from models.account import PortfolioAccount
from models.stored_holding import StoredHolding

from services.portfolio_database import PortfolioDatabase
from services.holdings_database import HoldingsDatabase


TEST_DATABASE = (
    r"D:\PMPH\data\test_holdings_storage.db"
)


def main():

    print("=" * 72)
    print("PMPH PERSISTENT HOLDINGS DATABASE TEST")
    print("=" * 72)

    if os.path.exists(
        TEST_DATABASE
    ):

        os.remove(
            TEST_DATABASE
        )

    # =====================================================
    # CREATE DATABASE + ACCOUNT
    # =====================================================

    portfolio_database = (
        PortfolioDatabase(
            TEST_DATABASE
        )
    )

    account = (
        portfolio_database.save_account(
            PortfolioAccount(
                owner_name="Test Owner",
                platform_name="Test Platform",
                account_name="Test Account",
            )
        )
    )

    holdings_database = (
        HoldingsDatabase(
            TEST_DATABASE
        )
    )

    print()
    print(
        "Account Created:",
        account.display_name()
    )

    # =====================================================
    # FIRST IMPORT
    # =====================================================

    first_holding = StoredHolding(
        account_id=account.account_id,
        symbol="MIDCAP",
        name="MIDCAP ETF",
        isin="INF000TEST01",
        asset_type="ETF",
        quantity=100.0,
        average_price=20.0,
        current_price=22.0,
        invested_value=2000.0,
        current_value=2200.0,
        profit_loss=200.0,
        profit_loss_percent=10.0,
        source_file="first_statement.xlsx",
    )

    saved_first = (
        holdings_database.save_holding(
            first_holding
        )
    )

    print()
    print(
        "Holdings After First Import:",
        holdings_database.count_holdings()
    )

    first_id = (
        saved_first.holding_id
    )

    # =====================================================
    # SECOND IMPORT OF SAME SECURITY
    # =====================================================

    updated_holding = StoredHolding(
        account_id=account.account_id,
        symbol="MIDCAP",
        name="MIDCAP ETF",
        isin="INF000TEST01",
        asset_type="ETF",
        quantity=125.0,
        average_price=20.50,
        current_price=23.0,
        invested_value=2562.50,
        current_value=2875.0,
        profit_loss=312.50,
        profit_loss_percent=12.1951,
        source_file="new_statement.xlsx",
    )

    saved_updated = (
        holdings_database.save_holding(
            updated_holding
        )
    )

    print(
        "Holdings After Re-Import:",
        holdings_database.count_holdings()
    )

    print(
        "Same Holding ID Preserved:",
        (
            saved_updated.holding_id
            == first_id
        )
    )

    # =====================================================
    # VERIFY UPDATED VALUES
    # =====================================================

    holdings = (
        holdings_database.list_holdings(
            account.account_id
        )
    )

    stored = holdings[0]

    print()
    print("-" * 72)

    print(
        "Stored Symbol:",
        stored.symbol
    )

    print(
        "Stored ISIN:",
        stored.isin
    )

    print(
        "Updated Quantity:",
        stored.quantity
    )

    print(
        "Updated Average Price:",
        stored.average_price
    )

    print(
        "Latest Source File:",
        stored.source_file
    )

    print()
    print("-" * 72)

    print(
        "Duplicate Prevention:",
        (
            "PASS"
            if holdings_database.count_holdings()
            == 1
            else "FAIL"
        )
    )

    print(
        "Snapshot Update:",
        (
            "PASS"
            if stored.quantity
            == 125.0
            else "FAIL"
        )
    )

    print(
        "Stable Holding Identity:",
        (
            "PASS"
            if stored.holding_id
            == first_id
            else "FAIL"
        )
    )

    print()
    print("=" * 72)
    print("HOLDINGS DATABASE TEST COMPLETE")
    print("=" * 72)


if __name__ == "__main__":

    main()