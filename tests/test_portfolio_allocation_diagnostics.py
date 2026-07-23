from pathlib import Path

from models.account import PortfolioAccount
from models.stored_holding import StoredHolding
from services.holdings_database import HoldingsDatabase
from services.portfolio_analytics_service import (
    PortfolioAnalyticsService,
)
from services.portfolio_database import PortfolioDatabase


def create_holding(
    account_id,
    symbol,
    current_value,
    asset_type,
):

    quantity = 10.0

    return StoredHolding(
        account_id=account_id,
        symbol=symbol,
        name=symbol,
        asset_type=asset_type,
        quantity=quantity,
        average_price=10.0,
        current_price=(
            current_value / quantity
        ),
        invested_value=100.0,
        current_value=current_value,
        profit_loss=(
            current_value - 100.0
        ),
        profit_loss_percent=0.0,
    )


def main():

    print("=" * 76)
    print(
        "PMPH PORTFOLIO ALLOCATION DIAGNOSTICS TEST"
    )
    print("=" * 76)

    database_path = str(
        Path("data")
        / "test_portfolio_allocation_diagnostics.db"
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

    analytics_service = (
        PortfolioAnalyticsService(
            database_path=database_path,
        )
    )

    # =====================================================
    # EMPTY IMPORTED PORTFOLIO
    # =====================================================

    empty_diagnostics = (
        analytics_service
        .get_allocation_diagnostics()
    )

    empty_portfolio_pass = (
        empty_diagnostics[
            "portfolio_current_value"
        ] == 0
        and empty_diagnostics[
            "security_count"
        ] == 0
        and empty_diagnostics[
            "account_count"
        ] == 0
        and empty_diagnostics[
            "asset_type_count"
        ] == 0
        and empty_diagnostics[
            "diagnostic_count"
        ] == 0
        and empty_diagnostics[
            "diagnostics"
        ] == []
    )

    empty_scope_pass = (
        empty_diagnostics[
            "allocation_scope"
        ] == "IMPORTED_PERSISTED_HOLDINGS"
        and empty_diagnostics[
            "portfolio_completeness"
        ] == "NOT_CONFIRMED"
    )

    # =====================================================
    # CREATE TWO ACCOUNTS
    # =====================================================

    account_one = (
        portfolio_database
        .save_account(
            PortfolioAccount(
                owner_name="Owner One",
                platform_name="Broker One",
                account_name="Account One",
            )
        )
    )

    account_two = (
        portfolio_database
        .save_account(
            PortfolioAccount(
                owner_name="Owner Two",
                platform_name="Broker Two",
                account_name="Account Two",
            )
        )
    )

    # =====================================================
    # DETERMINISTIC IMPORTED HOLDINGS FIXTURE
    #
    # Securities = 40 / 30 / 20 / 10
    # Account One = 70%
    # Account Two = 30%
    # ETF = 70%
    # GOLD = 20%
    # EQUITY = 10%
    #
    # IMPORTANT:
    # These holdings represent imported persisted holdings.
    # They must not be assumed to represent a complete
    # investor portfolio.
    # =====================================================

    holdings = [
        create_holding(
            account_one.account_id,
            "ALPHA",
            400.0,
            "ETF",
        ),
        create_holding(
            account_one.account_id,
            "BETA",
            300.0,
            "ETF",
        ),
        create_holding(
            account_two.account_id,
            "GAMMA",
            200.0,
            "GOLD",
        ),
        create_holding(
            account_two.account_id,
            "DELTA",
            100.0,
            "EQUITY",
        ),
    ]

    for holding in holdings:

        holdings_database.save_holding(
            holding
        )

    diagnostics = (
        analytics_service
        .get_allocation_diagnostics()
    )

    diagnostic_rows = {
        row["code"]: row
        for row in diagnostics[
            "diagnostics"
        ]
    }

    # =====================================================
    # DIAGNOSTIC CONTRACT
    # =====================================================

    expected_codes = {
        "LARGEST_SECURITY_POSITION",
        "TOP_THREE_SECURITY_ALLOCATION",
        "LARGEST_ACCOUNT_ALLOCATION",
        "LARGEST_ASSET_TYPE_ALLOCATION",
    }

    diagnostic_contract_pass = (
        set(
            diagnostic_rows.keys()
        )
        == expected_codes
        and diagnostics[
            "diagnostic_count"
        ] == 4
        and diagnostics[
            "security_count"
        ] == 4
        and diagnostics[
            "account_count"
        ] == 2
        and diagnostics[
            "asset_type_count"
        ] == 3
        and abs(
            diagnostics[
                "portfolio_current_value"
            ]
            - 1000.0
        ) < 0.000001
    )

    # =====================================================
    # DIAGNOSTIC VALUES
    # =====================================================

    diagnostic_values_pass = (
        diagnostic_rows[
            "LARGEST_SECURITY_POSITION"
        ]["symbol"] == "ALPHA"
        and abs(
            diagnostic_rows[
                "LARGEST_SECURITY_POSITION"
            ]["observed_value"]
            - 40.0
        ) < 0.000001
        and abs(
            diagnostic_rows[
                "TOP_THREE_SECURITY_ALLOCATION"
            ]["observed_value"]
            - 90.0
        ) < 0.000001
        and abs(
            diagnostic_rows[
                "LARGEST_ACCOUNT_ALLOCATION"
            ]["observed_value"]
            - 70.0
        ) < 0.000001
        and diagnostic_rows[
            "LARGEST_ASSET_TYPE_ALLOCATION"
        ]["asset_type"] == "ETF"
        and abs(
            diagnostic_rows[
                "LARGEST_ASSET_TYPE_ALLOCATION"
            ]["observed_value"]
            - 70.0
        ) < 0.000001
    )

    # =====================================================
    # IMPORTED PORTFOLIO SCOPE BOUNDARY
    # =====================================================

    imported_scope_pass = (
        diagnostics[
            "allocation_scope"
        ] == "IMPORTED_PERSISTED_HOLDINGS"
        and diagnostics[
            "portfolio_completeness"
        ] == "NOT_CONFIRMED"
        and bool(
            diagnostics[
                "scope_description"
            ]
        )
    )

    # =====================================================
    # RECOMMENDATION / INTELLIGENCE BOUNDARIES
    # =====================================================

    recommendation_boundary_pass = (
        diagnostics[
            "target_allocation"
        ] == "NOT_DEFINED"
        and diagnostics[
            "recommendation_status"
        ] == "NOT_PROVIDED"
        and diagnostics[
            "underlying_diversification"
        ] == "NOT_AVAILABLE"
        and diagnostics[
            "fund_etf_overlap"
        ] == "NOT_AVAILABLE"
    )

    print()
    print("-" * 76)

    print(
        "Empty Imported Portfolio:",
        "PASS"
        if empty_portfolio_pass
        else "FAIL",
    )

    print(
        "Empty Portfolio Scope Boundary:",
        "PASS"
        if empty_scope_pass
        else "FAIL",
    )

    print(
        "Allocation Diagnostics Contract:",
        "PASS"
        if diagnostic_contract_pass
        else "FAIL",
    )

    print(
        "Allocation Diagnostic Values:",
        "PASS"
        if diagnostic_values_pass
        else "FAIL",
    )

    print(
        "Imported Portfolio Scope:",
        "PASS"
        if imported_scope_pass
        else "FAIL",
    )

    print(
        "Recommendation Boundary:",
        "PASS"
        if recommendation_boundary_pass
        else "FAIL",
    )

    all_pass = all(
        [
            empty_portfolio_pass,
            empty_scope_pass,
            diagnostic_contract_pass,
            diagnostic_values_pass,
            imported_scope_pass,
            recommendation_boundary_pass,
        ]
    )

    print()
    print("=" * 76)

    if not all_pass:

        raise AssertionError(
            "Portfolio Allocation Diagnostics test failed."
        )

    print(
        "SPRINT 0.9.2 PORTFOLIO ALLOCATION DIAGNOSTICS TEST: PASS"
    )

    print("=" * 76)


if __name__ == "__main__":

    main()