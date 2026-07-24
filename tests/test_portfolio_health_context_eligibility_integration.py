from services.portfolio_health_context_requirements_service import (
    PortfolioHealthContextRequirementsService,
)
from services.portfolio_health_severity_service import (
    PortfolioHealthSeverityService,
)


def print_result(
    name,
    passed,
):
    if not passed:
        raise AssertionError(
            f"{name}: FAILED"
        )

    print(
        f"{name}: PASS"
    )


def main():

    print()
    print("=" * 76)
    print(
        "PMPH PORTFOLIO HEALTH CONTEXT "
        "ELIGIBILITY INTEGRATION TEST"
    )
    print("=" * 76)

    context_service = (
        PortfolioHealthContextRequirementsService()
    )

    severity_service = (
        PortfolioHealthSeverityService()
    )

    # =====================================================
    # NO CONTEXT AVAILABLE
    # =====================================================

    no_context = (
        context_service
        .evaluate_context_availability()
    )

    no_context_eligibility = (
        severity_service
        .evaluate_rule_context_eligibility(
            no_context
        )
    )

    print_result(
        "No Context Rule Count",
        no_context_eligibility[
            "rule_count"
        ] == 4,
    )

    print_result(
        "No Context Eligible Rules",
        no_context_eligibility[
            "context_eligible_rule_count"
        ] == 0,
    )

    print_result(
        "No Context Ineligible Rules",
        no_context_eligibility[
            "context_ineligible_rule_count"
        ] == 4,
    )

    print_result(
        "No Context Eligibility Status",
        no_context_eligibility[
            "eligibility_status"
        ] == "CONTEXT_REQUIREMENTS_INCOMPLETE",
    )

    # =====================================================
    # INSTRUMENT CONTEXT ONLY
    # =====================================================

    instrument_context = (
        context_service
        .evaluate_context_availability(
            [
                "INSTRUMENT_IDENTITY",
                "INSTRUMENT_CLASSIFICATION",
                "INVESTMENT_STRUCTURE",
            ]
        )
    )

    instrument_eligibility = (
        severity_service
        .evaluate_rule_context_eligibility(
            instrument_context
        )
    )

    instrument_map = {
        item[
            "observation_code"
        ]: item
        for item in instrument_eligibility[
            "rule_evaluations"
        ]
    }

    print_result(
        "Instrument Context Eligible Rule Count",
        instrument_eligibility[
            "context_eligible_rule_count"
        ] == 2,
    )

    print_result(
        "Largest Security Context Eligible",
        instrument_map[
            "LARGEST_SECURITY_POSITION"
        ][
            "context_eligibility_status"
        ] == "CONTEXT_ELIGIBLE",
    )

    print_result(
        "Top Three Context Eligible",
        instrument_map[
            "TOP_THREE_SECURITY_ALLOCATION"
        ][
            "context_eligibility_status"
        ] == "CONTEXT_ELIGIBLE",
    )

    print_result(
        "Account Context Still Ineligible",
        instrument_map[
            "LARGEST_ACCOUNT_ALLOCATION"
        ][
            "context_eligibility_status"
        ] == "CONTEXT_INELIGIBLE",
    )

    print_result(
        "Asset Type Context Still Ineligible",
        instrument_map[
            "LARGEST_ASSET_TYPE_ALLOCATION"
        ][
            "context_eligibility_status"
        ] == "CONTEXT_INELIGIBLE",
    )

    # =====================================================
    # ALL SYNTHETIC CONTEXT AVAILABLE
    # =====================================================

    all_context = (
        context_service
        .evaluate_context_availability(
            [
                "INSTRUMENT_IDENTITY",
                "INSTRUMENT_CLASSIFICATION",
                "INVESTMENT_STRUCTURE",
                "UNDERLYING_HOLDINGS",
                "ECONOMIC_EXPOSURE",
                "DIVERSIFICATION_CONTEXT",
                "OVERLAP_CONTEXT",
                "ACCOUNT_ROLE",
                "ACCOUNT_RISK_SEMANTICS",
            ]
        )
    )

    all_context_eligibility = (
        severity_service
        .evaluate_rule_context_eligibility(
            all_context
        )
    )

    print_result(
        "All Context Eligible Rule Count",
        all_context_eligibility[
            "context_eligible_rule_count"
        ] == 4,
    )

    print_result(
        "All Context Ineligible Rule Count",
        all_context_eligibility[
            "context_ineligible_rule_count"
        ] == 0,
    )

    print_result(
        "All Context Requirements Satisfied",
        all_context_eligibility[
            "eligibility_status"
        ] == "CONTEXT_REQUIREMENTS_SATISFIED",
    )

    # =====================================================
    # CRITICAL SEVERITY BOUNDARY
    # =====================================================

    print_result(
        "No Severity Output Eligible Rules",
        all_context_eligibility[
            "severity_output_eligible_rule_count"
        ] == 0,
    )

    print_result(
        "Severity Rules Still Not Defined",
        all_context_eligibility[
            "severity_rule_status"
        ] == "RULES_NOT_DEFINED",
    )

    print_result(
        "Context Eligibility Does Not Define Severity",
        all(
            item[
                "severity_rule_defined"
            ] is False
            and item[
                "severity_output_eligible"
            ] is False
            and item[
                "severity_rule_status"
            ] == "DEFERRED"
            for item in all_context_eligibility[
                "rule_evaluations"
            ]
        ),
    )

    # =====================================================
    # EXISTING SEVERITY OUTPUT MUST REMAIN EMPTY
    # =====================================================

    severity_output = (
        severity_service
        .classify_severity(
            [
                {
                    "observation_code": (
                        "LARGEST_SECURITY_POSITION"
                    ),
                    "classification": (
                        "SECURITY_CONCENTRATION"
                    ),
                    "observed_value": 53.48,
                }
            ]
        )
    )

    print_result(
        "No Premature Severity Classification",
        severity_output[
            "severity_classifications"
        ] == [],
    )

    print_result(
        "No Premature Severity Count",
        severity_output[
            "severity_classification_count"
        ] == 0,
    )

    # =====================================================
    # ARCHITECTURE BOUNDARIES
    # =====================================================

    print_result(
        "Imported Portfolio Scope",
        all_context_eligibility[
            "severity_scope"
        ] == "IMPORTED_PERSISTED_HOLDINGS",
    )

    print_result(
        "Portfolio Completeness Boundary",
        all_context_eligibility[
            "portfolio_completeness"
        ] == "NOT_CONFIRMED",
    )

    print_result(
        "Health Score Boundary",
        all_context_eligibility[
            "health_score"
        ] == "NOT_AVAILABLE",
    )

    print_result(
        "Target Allocation Boundary",
        all_context_eligibility[
            "target_allocation"
        ] == "NOT_DEFINED",
    )

    print_result(
        "Recommendation Boundary",
        all_context_eligibility[
            "recommendation_status"
        ] == "NOT_PROVIDED",
    )

    print()
    print("=" * 76)
    print(
        "SPRINT 0.9.6 PORTFOLIO HEALTH "
        "CONTEXT ELIGIBILITY INTEGRATION TEST: PASS"
    )
    print("=" * 76)


if __name__ == "__main__":
    main()
