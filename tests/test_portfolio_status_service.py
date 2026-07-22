from datetime import datetime
from pathlib import Path

from models.account import PortfolioAccount
from models.stored_holding import StoredHolding
from services.portfolio_database import PortfolioDatabase
from services.holdings_database import HoldingsDatabase
from services.portfolio_status_service import (
    PortfolioStatusService,
)


def create_account(
    portfolio_database,
):
    account = PortfolioAccount(
        owner_name="Test Owner",
        platform_name="Test Broker",
        account_name="Test Account",
    )

    return portfolio_database.save_account(
        account
    )


def create_holding(
    account_id,
    symbol,
    quantity,
    current_price,
    current_value,
    source_file,
):
    return StoredHolding(
        account_id=account_id,
        symbol=symbol,
        name=symbol,
        asset_type="ETF",
        quantity=quantity,
        average_price=10.0,
        current_price=current_price,
        invested_value=(
            quantity
            * 10.0
        ),
        current_value=current_value,
        profit_loss=(
            current_value
            - (
                quantity
                * 10.0
            )
        ),
        profit_loss_percent=0.0,
        source_file=source_file,
    )


def main():

    print("=" * 76)
    print(
        "PMPH PORTFOLIO STATUS SERVICE TEST"
    )
    print("=" * 76)

    database_path = str(
        Path("data")
        / "test_portfolio_status.db"
    )

    test_database = Path(
        database_path
    )

    if test_database.exists():

        test_database.unlink()

    portfolio_database = PortfolioDatabase(
        database_path=database_path,
    )

    holdings_database = HoldingsDatabase(
        database_path=database_path,
    )

    status_service = PortfolioStatusService(
        database_path=database_path,
    )

    # -------------------------------------------------
    # EMPTY PORTFOLIO
    # -------------------------------------------------

    empty_status = (
        status_service
        .get_portfolio_status()
    )

    empty_pass = (
        empty_status["holding_count"] == 0
        and empty_status[
            "valuation_covered_count"
        ] == 0
        and empty_status[
            "valuation_coverage_percent"
        ] == 0.0
        and empty_status[
            "latest_record_update"
        ] is None
        and empty_status[
            "oldest_record_update"
        ] is None
        and empty_status[
            "market_valuation_freshness"
        ] == "NOT_TRACKED"
        and empty_status[
            "market_valuation_as_of"
        ] is None
    )

    print()
    print("EMPTY PORTFOLIO")
    print("-" * 76)
    print(
        "Empty Portfolio Status:",
        "PASS"
        if empty_pass
        else "FAIL",
    )

    # -------------------------------------------------
    # TEST HOLDINGS
    # -------------------------------------------------

    account = create_account(
        portfolio_database
    )

    valid_one = create_holding(
        account.account_id,
        "VALID1",
        10.0,
        20.0,
        200.0,
        "statement_a.xlsx",
    )

    valid_two = create_holding(
        account.account_id,
        "VALID2",
        5.0,
        30.0,
        150.0,
        "statement_a.xlsx",
    )

    invalid_one = create_holding(
        account.account_id,
        "INVALID1",
        10.0,
        20.0,
        999.0,
        "statement_b.xlsx",
    )

    holdings_database.save_holding(
        valid_one
    )

    holdings_database.save_holding(
        valid_two
    )

    holdings_database.save_holding(
        invalid_one
    )

    status = (
        status_service
        .get_portfolio_status()
    )

    # -------------------------------------------------
    # ASSERTIONS
    # -------------------------------------------------

    count_pass = (
        status["holding_count"]
        == 3
    )

    coverage_pass = (
        status[
            "valuation_covered_count"
        ] == 2
        and abs(
            status[
                "valuation_coverage_percent"
            ]
            - (
                2
                / 3
                * 100.0
            )
        ) < 0.0001
    )

    source_pass = (
        status[
            "source_file_count"
        ] == 2
        and status[
            "source_files"
        ] == [
            "statement_a.xlsx",
            "statement_b.xlsx",
        ]
    )

    timestamp_pass = (
        isinstance(
            status[
                "latest_record_update"
            ],
            datetime,
        )
        and isinstance(
            status[
                "oldest_record_update"
            ],
            datetime,
        )
        and status[
            "latest_record_update"
        ]
        >= status[
            "oldest_record_update"
        ]
    )

    freshness_pass = (
        status[
            "market_valuation_freshness"
        ] == "NOT_TRACKED"
        and status[
            "market_valuation_as_of"
        ] is None
    )

    print()
    print("PERSISTED PORTFOLIO STATUS")
    print("-" * 76)

    print(
        "Holding Count:",
        status["holding_count"],
    )

    print(
        "Valuation Covered:",
        status[
            "valuation_covered_count"
        ],
    )

    print(
        "Valuation Coverage %:",
        round(
            status[
                "valuation_coverage_percent"
            ],
            2,
        ),
    )

    print(
        "Source Files:",
        status[
            "source_files"
        ],
    )

    print(
        "Latest Record Update:",
        status[
            "latest_record_update"
        ],
    )

    print(
        "Oldest Record Update:",
        status[
            "oldest_record_update"
        ],
    )

    print(
        "Market Valuation Freshness:",
        status[
            "market_valuation_freshness"
        ],
    )

    print()
    print("-" * 76)

    print(
        "Holding Count:",
        "PASS"
        if count_pass
        else "FAIL",
    )

    print(
        "Valuation Coverage:",
        "PASS"
        if coverage_pass
        else "FAIL",
    )

    print(
        "Source File Deduplication:",
        "PASS"
        if source_pass
        else "FAIL",
    )

    print(
        "Record Update Timestamps:",
        "PASS"
        if timestamp_pass
        else "FAIL",
    )

    print(
        "Market Freshness Boundary:",
        "PASS"
        if freshness_pass
        else "FAIL",
    )

    all_pass = all(
        [
            empty_pass,
            count_pass,
            coverage_pass,
            source_pass,
            timestamp_pass,
            freshness_pass,
        ]
    )

    print()
    print("=" * 76)

    if not all_pass:

        raise AssertionError(
            "Portfolio Status Service test failed."
        )

    print(
        "SPRINT 0.8.2 PORTFOLIO STATUS SERVICE TEST: PASS"
    )

    print("=" * 76)


if __name__ == "__main__":

    main()
