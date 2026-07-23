from pathlib import Path

from models.account import PortfolioAccount
from models.stored_holding import StoredHolding
from services.holdings_database import HoldingsDatabase
from services.portfolio_database import PortfolioDatabase
from services.portfolio_health_service import (
    PortfolioHealthService,
)


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
        "PMPH PORTFOLIO HEALTH SERVICE TEST"
    )
    print("=" * 76)

    database_path = str(
        Path("data")
        / "test_portfolio_health_service.db"
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

    health_service = PortfolioHealthService(
        database_path=database_path,
    )

    # =====================================================
    # EMPTY PORTFOLIO CONTRACT
    # =====================================================

    empty_health = (
        health_service
        .get_health_diagnostics()
    )

    empty_portfolio_pass = (
        empty_health[
            "portfolio_current_value"
        ] == 0
        and empty_health[
            "security_count"
        ] == 0
        and empty_health[
            "account_count"
        ] == 0
        and empty_health[
            "asset_type_count"
        ] == 0
        and empty_health[
            "observation_count"
        ] == 0
        and empty_health[
            "observations"
        ] == []
    )

    empty_boundary_pass = (
        empty_health[
            "framework"
        ]
        == "PORTFOLIO_HEALTH_DIAGNOSTIC_FOUNDATION"
        and empty_health[
            "framework_status"
        ]
        == "OBSERVATION_ONLY"
        and empty_health[
            "analysis_scope"
        ]
        == "IMPORTED_PERSISTED_HOLDINGS"
        and empty_health[
            "portfolio_completeness"
        ]
        == "NOT_CONFIRMED"
        and empty_health[
            "complete_portfolio_analytics"
        ]
        == "NOT_AVAILABLE"
    )

    # =====================================================
    # CREATE TEST PORTFOLIO
    #
    # 40 / 30 / 20 / 10
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

    health = (
        health_service
        .get_health_diagnostics()
    )

    # =====================================================
    # FRAMEWORK CONTRACT
    # =====================================================

    framework_pass = (
        health[
            "framework"
        ]
        == "PORTFOLIO_HEALTH_DIAGNOSTIC_FOUNDATION"
        and health[
            "framework_status"
        ]
        == "OBSERVATION_ONLY"
        and health[
            "portfolio_current_value"
        ] == 1000.0
        and health[
            "security_count"
        ] == 4
        and health[
            "account_count"
        ] == 2
        and health[
            "asset_type_count"
        ] == 3
    )

    # =====================================================
    # OBSERVATION CONTRACT
    # =====================================================

    observation_codes = [
        observation["code"]
        for observation in health[
            "observations"
        ]
    ]

    observation_pass = (
        health[
            "observation_count"
        ] == 4
        and observation_codes
        == [
            "LARGEST_SECURITY_POSITION",
            "TOP_THREE_SECURITY_ALLOCATION",
            "LARGEST_ACCOUNT_ALLOCATION",
            "LARGEST_ASSET_TYPE_ALLOCATION",
        ]
        and all(
            observation[
                "source"
            ]
            == "ALLOCATION_DIAGNOSTICS"
            for observation in health[
                "observations"
            ]
        )
    )

    # =====================================================
    # CONCENTRATION METRICS
    # =====================================================

    metrics = health[
        "concentration_metrics"
    ]

    metrics_pass = (
        abs(
            metrics[
                "largest_position_percent"
            ]
            - 40.0
        )
        < 0.000001
        and abs(
            metrics[
                "top_3_percent"
            ]
            - 90.0
        )
        < 0.000001
        and abs(
            metrics[
                "largest_account_percent"
            ]
            - 70.0
        )
        < 0.000001
    )

    # =====================================================
    # SCOPE AND SAFETY BOUNDARIES
    # =====================================================

    scope_pass = (
        health[
            "analysis_scope"
        ]
        == "IMPORTED_PERSISTED_HOLDINGS"
        and health[
            "portfolio_completeness"
        ]
        == "NOT_CONFIRMED"
        and health[
            "complete_portfolio_analytics"
        ]
        == "NOT_AVAILABLE"
    )

    scoring_boundary_pass = (
        health[
            "health_score"
        ]
        == "NOT_AVAILABLE"
        and health[
            "target_allocation"
        ]
        == "NOT_DEFINED"
        and health[
            "recommendation_status"
        ]
        == "NOT_PROVIDED"
    )

    deferred_analytics_pass = (
        health[
            "underlying_diversification"
        ]
        == "NOT_AVAILABLE"
        and health[
            "fund_etf_overlap"
        ]
        == "NOT_AVAILABLE"
        and health[
            "market_dependent_analytics"
        ]
        == "NOT_AVAILABLE"
    )

    print()
    print("-" * 76)

    checks = [
        (
            "Empty Portfolio Contract",
            empty_portfolio_pass,
        ),
        (
            "Empty Scope Boundary",
            empty_boundary_pass,
        ),
        (
            "Health Framework Contract",
            framework_pass,
        ),
        (
            "Diagnostic Observations",
            observation_pass,
        ),
        (
            "Concentration Metrics",
            metrics_pass,
        ),
        (
            "Imported Portfolio Scope",
            scope_pass,
        ),
        (
            "Scoring and Recommendation Boundary",
            scoring_boundary_pass,
        ),
        (
            "Deferred Analytics Boundary",
            deferred_analytics_pass,
        ),
    ]

    for label, passed in checks:
        print(
            f"{label}:",
            "PASS"
            if passed
            else "FAIL",
        )

    all_pass = all(
        passed
        for _, passed in checks
    )

    print()
    print("=" * 76)

    if not all_pass:
        raise AssertionError(
            "Portfolio Health Service test failed."
        )

    print(
        "SPRINT 0.9.3 PORTFOLIO HEALTH SERVICE TEST: PASS"
    )

    print("=" * 76)

    del health_service
    del holdings_database
    del portfolio_database

    import gc
    import time

    gc.collect()

    for attempt in range(5):

        if not test_database.exists():
            break

        try:
            test_database.unlink()
            break

        except PermissionError:

            if attempt == 4:
                raise

            time.sleep(0.2)


if __name__ == "__main__":

    main()
