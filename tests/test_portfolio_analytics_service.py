from pathlib import Path

from models.account import PortfolioAccount
from models.stored_holding import StoredHolding
from services.portfolio_database import PortfolioDatabase
from services.holdings_database import HoldingsDatabase
from services.portfolio_analytics_service import (
    PortfolioAnalyticsService,
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
        "PMPH PORTFOLIO ANALYTICS SERVICE TEST"
    )
    print("=" * 76)

    database_path = str(
        Path("data")
        / "test_portfolio_analytics.db"
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
    # EMPTY PORTFOLIO
    # =====================================================

    empty_security = (
        analytics_service
        .get_security_concentration()
    )

    empty_summary = (
        analytics_service
        .get_concentration_summary()
    )

    empty_pass = (
        empty_security["security_count"] == 0
        and empty_security[
            "total_current_value"
        ] == 0
        and empty_security[
            "largest_position_percent"
        ] == 0
        and empty_security[
            "top_3_percent"
        ] == 0
        and empty_security["hhi"] == 0
        and empty_security[
            "effective_security_positions"
        ] == 0
        and empty_summary[
            "underlying_diversification"
        ] == "NOT_AVAILABLE"
        and empty_summary[
            "fund_etf_overlap"
        ] == "NOT_AVAILABLE"
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
    # DETERMINISTIC 40 / 30 / 20 / 10 PORTFOLIO
    #
    # Account One = 70%
    # Account Two = 30%
    #
    # ETF = 70%
    # GOLD = 20%
    # EQUITY = 10%
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

    security = (
        analytics_service
        .get_security_concentration()
    )

    account = (
        analytics_service
        .get_account_concentration()
    )

    asset_type = (
        analytics_service
        .get_asset_type_concentration()
    )

    summary = (
        analytics_service
        .get_concentration_summary()
    )

    # =====================================================
    # SECURITY TESTS
    # =====================================================

    positions = security[
        "positions"
    ]

    ranking_pass = (
        [
            row["symbol"]
            for row in positions
        ]
        == [
            "ALPHA",
            "BETA",
            "GAMMA",
            "DELTA",
        ]
    )

    weights_pass = all(
        abs(
            actual - expected
        ) < 0.000001
        for actual, expected in zip(
            [
                row["weight_percent"]
                for row in positions
            ],
            [
                40.0,
                30.0,
                20.0,
                10.0,
            ],
        )
    )

    top_concentration_pass = (
        abs(
            security[
                "largest_position_percent"
            ]
            - 40.0
        )
        < 0.000001
        and abs(
            security[
                "top_3_percent"
            ]
            - 90.0
        )
        < 0.000001
    )

    expected_hhi = (
        0.4 ** 2
        + 0.3 ** 2
        + 0.2 ** 2
        + 0.1 ** 2
    )

    hhi_pass = (
        abs(
            security["hhi"]
            - expected_hhi
        )
        < 0.000001
    )

    effective_positions_pass = (
        abs(
            security[
                "effective_security_positions"
            ]
            - (
                1.0 / expected_hhi
            )
        )
        < 0.000001
    )

    scope_pass = (
        security["scope"]
        == "PERSISTED_SECURITY_POSITIONS"
    )

    # =====================================================
    # ACCOUNT TESTS
    # =====================================================

    account_pass = (
        account["account_count"] == 2
        and abs(
            account[
                "largest_account_percent"
            ]
            - 70.0
        )
        < 0.000001
        and abs(
            account["hhi"]
            - (
                0.7 ** 2
                + 0.3 ** 2
            )
        )
        < 0.000001
    )

    # =====================================================
    # ASSET TYPE TESTS
    # =====================================================

    asset_rows = {
        row["asset_type"]:
        row["weight_percent"]
        for row in asset_type[
            "asset_types"
        ]
    }

    asset_type_pass = (
        asset_type[
            "asset_type_count"
        ] == 3
        and abs(
            asset_rows["ETF"]
            - 70.0
        )
        < 0.000001
        and abs(
            asset_rows["GOLD"]
            - 20.0
        )
        < 0.000001
        and abs(
            asset_rows["EQUITY"]
            - 10.0
        )
        < 0.000001
        and asset_type["scope"]
        == "PERSISTED_ASSET_TYPE_METADATA"
    )

    # =====================================================
    # ANALYTICS BOUNDARY TESTS
    # =====================================================

    boundary_pass = (
        summary[
            "underlying_diversification"
        ] == "NOT_AVAILABLE"
        and summary[
            "fund_etf_overlap"
        ] == "NOT_AVAILABLE"
    )

    print()
    print("-" * 76)

    print(
        "Empty Portfolio:",
        "PASS"
        if empty_pass
        else "FAIL",
    )

    print(
        "Security Ranking:",
        "PASS"
        if ranking_pass
        else "FAIL",
    )

    print(
        "Security Weights:",
        "PASS"
        if weights_pass
        else "FAIL",
    )

    print(
        "Top Concentration:",
        "PASS"
        if top_concentration_pass
        else "FAIL",
    )

    print(
        "Security HHI:",
        "PASS"
        if hhi_pass
        else "FAIL",
    )

    print(
        "Effective Security Positions:",
        "PASS"
        if effective_positions_pass
        else "FAIL",
    )

    print(
        "Security Scope:",
        "PASS"
        if scope_pass
        else "FAIL",
    )

    print(
        "Account Concentration:",
        "PASS"
        if account_pass
        else "FAIL",
    )

    print(
        "Asset Type Concentration:",
        "PASS"
        if asset_type_pass
        else "FAIL",
    )

    print(
        "Analytics Boundaries:",
        "PASS"
        if boundary_pass
        else "FAIL",
    )

    all_pass = all(
        [
            empty_pass,
            ranking_pass,
            weights_pass,
            top_concentration_pass,
            hhi_pass,
            effective_positions_pass,
            scope_pass,
            account_pass,
            asset_type_pass,
            boundary_pass,
        ]
    )

    print()
    print("=" * 76)

    if not all_pass:

        raise AssertionError(
            "Portfolio Analytics Service test failed."
        )

    print(
        "SPRINT 0.9.1 PORTFOLIO ANALYTICS SERVICE TEST: PASS"
    )

    print("=" * 76)

if __name__ == "__main__":

    main()

