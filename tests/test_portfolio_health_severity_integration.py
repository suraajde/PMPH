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


def print_result(
    name,
    passed,
):

    status = (
        "PASS"
        if passed
        else "FAIL"
    )

    print(
        f"{name}: {status}"
    )

    if not passed:

        raise AssertionError(
            name
        )


def main():

    print("=" * 76)
    print(
        "PMPH PORTFOLIO HEALTH SEVERITY INTEGRATION TEST"
    )
    print("=" * 76)

    database_path = str(
        Path("data")
        / "test_portfolio_health_classification_integration.db"
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

    try:

        # =================================================
        # EMPTY PORTFOLIO INTEGRATED CONTRACT
        # =================================================

        empty_health = (
            health_service
            .get_health_diagnostics()
        )

        empty_contract_pass = (
            empty_health[
                "observations"
            ] == []
            and empty_health[
                "observation_count"
            ] == 0
            and empty_health[
                "classifications"
            ] == []
            and empty_health[
                "classification_count"
            ] == 0
        )

        print_result(
            "Empty Integrated Contract",
            empty_contract_pass,
        )

        empty_boundary_pass = (
            empty_health[
                "classification_status"
            ] == "DESCRIPTIVE_ONLY"
            and empty_health[
                "classification_scope"
            ] == "IMPORTED_PERSISTED_HOLDINGS"
            and empty_health[
                "portfolio_completeness"
            ] == "NOT_CONFIRMED"
            and empty_health[
                "severity_classification"
            ] == "NOT_DEFINED"
            and empty_health[
                "health_score"
            ] == "NOT_AVAILABLE"
            and empty_health[
                "target_allocation"
            ] == "NOT_DEFINED"
            and empty_health[
                "recommendation_status"
            ] == "NOT_PROVIDED"
        )

        print_result(
            "Empty Classification Boundary",
            empty_boundary_pass,
        )

        # =================================================
        # CREATE TWO ACCOUNTS
        # =================================================

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

        # =================================================
        # CREATE DETERMINISTIC PORTFOLIO
        # =================================================

        holdings = [
            create_holding(
                account_one.account_id,
                "SECURITY_A",
                400.0,
                "ETF",
            ),
            create_holding(
                account_one.account_id,
                "SECURITY_B",
                300.0,
                "ETF",
            ),
            create_holding(
                account_one.account_id,
                "SECURITY_C",
                200.0,
                "ETF",
            ),
            create_holding(
                account_two.account_id,
                "SECURITY_D",
                100.0,
                "ETF",
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

        # =================================================
        # OBSERVATION / CLASSIFICATION SEPARATION
        # =================================================

        observation_codes = {
            item[
                "code"
            ]
            for item in health[
                "observations"
            ]
        }

        classification_codes = {
            item[
                "observation_code"
            ]
            for item in health[
                "classifications"
            ]
        }

        expected_codes = {
            "LARGEST_SECURITY_POSITION",
            "TOP_THREE_SECURITY_ALLOCATION",
            "LARGEST_ACCOUNT_ALLOCATION",
            "LARGEST_ASSET_TYPE_ALLOCATION",
        }

        separation_pass = (
            health[
                "observation_count"
            ] == 4
            and health[
                "classification_count"
            ] == 4
            and observation_codes
            == expected_codes
            and classification_codes
            == expected_codes
        )

        print_result(
            "Observation Classification Separation",
            separation_pass,
        )

        # =================================================
        # CLASSIFICATION CONTRACT
        # =================================================

        classification_map = {
            item[
                "observation_code"
            ]: item
            for item in health[
                "classifications"
            ]
        }

        classification_contract_pass = (
            classification_map[
                "LARGEST_SECURITY_POSITION"
            ][
                "classification"
            ]
            == "SECURITY_CONCENTRATION"
            and classification_map[
                "TOP_THREE_SECURITY_ALLOCATION"
            ][
                "classification"
            ]
            == "SECURITY_CONCENTRATION"
            and classification_map[
                "LARGEST_ACCOUNT_ALLOCATION"
            ][
                "classification"
            ]
            == "ACCOUNT_CONCENTRATION"
            and classification_map[
                "LARGEST_ASSET_TYPE_ALLOCATION"
            ][
                "classification"
            ]
            == "ASSET_TYPE_CONCENTRATION"
        )

        print_result(
            "Deterministic Classification Integration",
            classification_contract_pass,
        )

        # =================================================
        # OBSERVED VALUE PRESERVATION
        # =================================================

        observation_values = {
            item[
                "code"
            ]: item[
                "observed_value"
            ]
            for item in health[
                "observations"
            ]
        }

        classification_values = {
            item[
                "observation_code"
            ]: item[
                "observed_value"
            ]
            for item in health[
                "classifications"
            ]
        }

        observed_value_pass = (
            observation_values
            == classification_values
        )

        print_result(
            "Observed Value Preservation",
            observed_value_pass,
        )

        # =================================================
        # SCOPE AND PROVENANCE
        # =================================================

        scope_provenance_pass = all(
            item[
                "classification_type"
            ] == "DESCRIPTIVE"
            and item[
                "classification_scope"
            ] == "IMPORTED_PERSISTED_HOLDINGS"
            and item[
                "provenance"
            ] == "DETERMINISTIC_DIAGNOSTIC_RULE"
            for item in health[
                "classifications"
            ]
        )

        print_result(
            "Classification Scope and Provenance",
            scope_provenance_pass,
        )

        # =================================================
        # SEVERITY ELIGIBILITY INTEGRATION
        # =================================================

        severity_contract_pass = (
            health[
                "severity_classifications"
            ] == []
            and health[
                "severity_classification_count"
            ] == 0
            and health[
                "severity_status"
            ] == "ELIGIBILITY_GATED"
            and health[
                "severity_scope"
            ] == "IMPORTED_PERSISTED_HOLDINGS"
            and health[
                "severity_rule_status"
            ] == "NO_ELIGIBLE_RULES"
        )

        print_result(
            "Severity Eligibility Integration",
            severity_contract_pass,
        )

        # =================================================
        # NO PREMATURE SEVERITY
        # =================================================

        no_premature_severity_pass = (
            health[
                "observation_count"
            ] == 4
            and health[
                "classification_count"
            ] == 4
            and health[
                "severity_classification_count"
            ] == 0
            and health[
                "severity_classifications"
            ] == []
        )

        print_result(
            "No Premature Severity",
            no_premature_severity_pass,
        )

        # =================================================
        # SEVERITY / SCORING / RECOMMENDATION SEPARATION
        # =================================================

        severity_boundary_pass = (
            health[
                "severity_classification"
            ] == "NOT_DEFINED"
            and health[
                "severity_status"
            ] == "ELIGIBILITY_GATED"
            and health[
                "health_score"
            ] == "NOT_AVAILABLE"
            and health[
                "target_allocation"
            ] == "NOT_DEFINED"
            and health[
                "recommendation_status"
            ] == "NOT_PROVIDED"
        )

        print_result(
            "Severity Architecture Separation",
            severity_boundary_pass,
        )

        # =================================================
        # ARCHITECTURE BOUNDARIES
        # =================================================

        boundary_pass = (
            health[
                "classification_status"
            ] == "DESCRIPTIVE_ONLY"
            and health[
                "classification_scope"
            ] == "IMPORTED_PERSISTED_HOLDINGS"
            and health[
                "portfolio_completeness"
            ] == "NOT_CONFIRMED"
            and health[
                "complete_portfolio_analytics"
            ] == "NOT_AVAILABLE"
            and health[
                "severity_classification"
            ] == "NOT_DEFINED"
            and health[
                "severity_classifications"
            ] == []
            and health[
                "severity_classification_count"
            ] == 0
            and health[
                "severity_status"
            ] == "ELIGIBILITY_GATED"
            and health[
                "severity_scope"
            ] == "IMPORTED_PERSISTED_HOLDINGS"
            and health[
                "severity_rule_status"
            ] == "NO_ELIGIBLE_RULES"
            and health[
                "health_score"
            ] == "NOT_AVAILABLE"
            and health[
                "target_allocation"
            ] == "NOT_DEFINED"
            and health[
                "recommendation_status"
            ] == "NOT_PROVIDED"
            and health[
                "underlying_diversification"
            ] == "NOT_AVAILABLE"
            and health[
                "fund_etf_overlap"
            ] == "NOT_AVAILABLE"
            and health[
                "market_dependent_analytics"
            ] == "NOT_AVAILABLE"
        )

        print_result(
            "Classification Architecture Boundary",
            boundary_pass,
        )

        print()
        print("=" * 76)
        print(
            "SPRINT 0.9.5 PORTFOLIO HEALTH "
            "SEVERITY INTEGRATION TEST: PASS"
        )
        print("=" * 76)

    finally:

        # Release service/database references before cleanup.
        health_service = None
        holdings_database = None
        portfolio_database = None

        import gc

        gc.collect()

        if test_database.exists():

            test_database.unlink()


if __name__ == "__main__":

    main()
