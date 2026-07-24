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
        "REQUIREMENTS SERVICE TEST"
    )
    print("=" * 76)

    context_service = (
        PortfolioHealthContextRequirementsService()
    )

    severity_service = (
        PortfolioHealthSeverityService()
    )

    registry = (
        context_service
        .get_requirement_registry()
    )

    # =====================================================
    # REGISTRY CONTRACT
    # =====================================================

    print_result(
        "Context Requirement Count",
        registry[
            "requirement_count"
        ] == 3,
    )

    print_result(
        "Available Requirement Count",
        registry[
            "available_requirement_count"
        ] == 0,
    )

    print_result(
        "Context Registry Status",
        registry[
            "registry_status"
        ] == "CONTEXT_REQUIREMENTS_DEFINED",
    )

    # =====================================================
    # REQUIRED CONTEXT FAMILIES
    # =====================================================

    requirement_map = {
        item[
            "data_requirement_status"
        ]: item
        for item in registry[
            "requirements"
        ]
    }

    expected_requirements = {
        "INSTRUMENT_INTELLIGENCE_REQUIRED",
        "UNDERLYING_EXPOSURE_MODEL_REQUIRED",
        "ACCOUNT_RISK_MODEL_REQUIRED",
    }

    print_result(
        "Required Context Families",
        set(
            requirement_map.keys()
        ) == expected_requirements,
    )

    # =====================================================
    # INSTRUMENT CONTEXT
    # =====================================================

    instrument = requirement_map[
        "INSTRUMENT_INTELLIGENCE_REQUIRED"
    ]

    print_result(
        "Instrument Context Type",
        instrument[
            "requirement_type"
        ] == "INSTRUMENT_CONTEXT",
    )

    print_result(
        "Instrument Context Capabilities",
        instrument[
            "required_capabilities"
        ] == [
            "INSTRUMENT_IDENTITY",
            "INSTRUMENT_CLASSIFICATION",
            "INVESTMENT_STRUCTURE",
        ],
    )

    # =====================================================
    # EXPOSURE CONTEXT
    # =====================================================

    exposure = requirement_map[
        "UNDERLYING_EXPOSURE_MODEL_REQUIRED"
    ]

    print_result(
        "Exposure Context Type",
        exposure[
            "requirement_type"
        ] == "EXPOSURE_CONTEXT",
    )

    print_result(
        "Exposure Context Capabilities",
        exposure[
            "required_capabilities"
        ] == [
            "UNDERLYING_HOLDINGS",
            "ECONOMIC_EXPOSURE",
            "DIVERSIFICATION_CONTEXT",
            "OVERLAP_CONTEXT",
        ],
    )

    # =====================================================
    # ACCOUNT CONTEXT
    # =====================================================

    account = requirement_map[
        "ACCOUNT_RISK_MODEL_REQUIRED"
    ]

    print_result(
        "Account Context Type",
        account[
            "requirement_type"
        ] == "ACCOUNT_CONTEXT",
    )

    print_result(
        "Account Context Capabilities",
        account[
            "required_capabilities"
        ] == [
            "ACCOUNT_ROLE",
            "ACCOUNT_RISK_SEMANTICS",
        ],
    )

    # =====================================================
    # AVAILABILITY BOUNDARY
    # =====================================================

    print_result(
        "No Premature Context Availability",
        all(
            item[
                "requirement_status"
            ] == "NOT_AVAILABLE"
            for item in registry[
                "requirements"
            ]
        ),
    )

    # =====================================================
    # SCOPE AND PROVENANCE
    # =====================================================

    print_result(
        "Context Scope",
        registry[
            "context_scope"
        ] == "IMPORTED_PERSISTED_HOLDINGS",
    )

    print_result(
        "Context Provenance",
        all(
            item[
                "provenance"
            ]
            == (
                "PORTFOLIO_HEALTH_"
                "CONTEXT_REQUIREMENT_REGISTRY"
            )
            for item in registry[
                "requirements"
            ]
        ),
    )

    # =====================================================
    # SEVERITY REGISTRY ALIGNMENT
    # =====================================================

    severity_registry = (
        severity_service
        .get_rule_registry()
    )

    severity_requirements = {
        rule[
            "data_requirement_status"
        ]
        for rule in severity_registry[
            "rules"
        ]
    }

    print_result(
        "Severity Context Requirement Coverage",
        severity_requirements
        == expected_requirements,
    )

    unresolved_mappings = [
        requirement
        for requirement
        in severity_requirements
        if context_service.get_requirement(
            requirement
        ) is None
    ]

    print_result(
        "Severity Requirement Mapping Complete",
        unresolved_mappings == [],
    )

    # =====================================================
    # CONTEXT AVAILABILITY EVALUATION
    # =====================================================

    no_capabilities = (
        context_service
        .evaluate_context_availability()
    )

    print_result(
        "No Capability Requirement Count",
        no_capabilities[
            "requirement_count"
        ] == 3,
    )

    print_result(
        "No Capability Availability",
        no_capabilities[
            "available_requirement_count"
        ] == 0
        and no_capabilities[
            "unavailable_requirement_count"
        ] == 3
        and no_capabilities[
            "availability_status"
        ] == "CONTEXT_INCOMPLETE",
    )

    # =====================================================
    # PARTIAL INSTRUMENT CONTEXT
    # =====================================================

    partial_instrument = (
        context_service
        .evaluate_context_availability(
            [
                "INSTRUMENT_IDENTITY",
                "INSTRUMENT_CLASSIFICATION",
            ]
        )
    )

    partial_map = {
        item[
            "data_requirement_status"
        ]: item
        for item
        in partial_instrument[
            "evaluations"
        ]
    }

    print_result(
        "Partial Instrument Context Remains Unavailable",
        partial_map[
            "INSTRUMENT_INTELLIGENCE_REQUIRED"
        ][
            "requirement_available"
        ] is False,
    )

    print_result(
        "Missing Investment Structure Detected",
        partial_map[
            "INSTRUMENT_INTELLIGENCE_REQUIRED"
        ][
            "missing_capabilities"
        ] == [
            "INVESTMENT_STRUCTURE",
        ],
    )

    # =====================================================
    # COMPLETE INSTRUMENT CONTEXT ONLY
    # =====================================================

    complete_instrument = (
        context_service
        .evaluate_context_availability(
            [
                "INSTRUMENT_IDENTITY",
                "INSTRUMENT_CLASSIFICATION",
                "INVESTMENT_STRUCTURE",
            ]
        )
    )

    complete_instrument_map = {
        item[
            "data_requirement_status"
        ]: item
        for item
        in complete_instrument[
            "evaluations"
        ]
    }

    print_result(
        "Instrument Context Becomes Available",
        complete_instrument_map[
            "INSTRUMENT_INTELLIGENCE_REQUIRED"
        ][
            "requirement_available"
        ] is True,
    )

    print_result(
        "Only Instrument Requirement Available",
        complete_instrument[
            "available_requirement_count"
        ] == 1
        and complete_instrument[
            "unavailable_requirement_count"
        ] == 2
        and complete_instrument[
            "availability_status"
        ] == "CONTEXT_INCOMPLETE",
    )

    # =====================================================
    # ALL REGISTERED CONTEXT CAPABILITIES
    # =====================================================

    all_capabilities = (
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

    print_result(
        "All Context Requirements Available",
        all_capabilities[
            "available_requirement_count"
        ] == 3
        and all_capabilities[
            "unavailable_requirement_count"
        ] == 0
        and all_capabilities[
            "availability_status"
        ] == "CONTEXT_AVAILABLE",
    )

    print_result(
        "Availability Evaluation Scope",
        all_capabilities[
            "context_scope"
        ] == "IMPORTED_PERSISTED_HOLDINGS",
    )

    print_result(
        "Availability Evaluation Boundaries",
        all_capabilities[
            "portfolio_completeness"
        ] == "NOT_CONFIRMED"
        and all_capabilities[
            "severity_status"
        ] == "NOT_EVALUATED"
        and all_capabilities[
            "health_score"
        ] == "NOT_AVAILABLE"
        and all_capabilities[
            "target_allocation"
        ] == "NOT_DEFINED"
        and all_capabilities[
            "recommendation_status"
        ] == "NOT_PROVIDED",
    )

    # =====================================================
    # UNKNOWN REQUIREMENT SAFETY
    # =====================================================

    print_result(
        "Unknown Requirement Safety",
        context_service.get_requirement(
            "UNKNOWN_REQUIREMENT"
        ) is None,
    )

    # =====================================================
    # ARCHITECTURE BOUNDARIES
    # =====================================================

    print_result(
        "Portfolio Completeness Boundary",
        registry[
            "portfolio_completeness"
        ] == "NOT_CONFIRMED",
    )

    print_result(
        "Severity Evaluation Boundary",
        registry[
            "severity_status"
        ] == "NOT_EVALUATED",
    )

    print_result(
        "Health Score Boundary",
        registry[
            "health_score"
        ] == "NOT_AVAILABLE",
    )

    print_result(
        "Target Allocation Boundary",
        registry[
            "target_allocation"
        ] == "NOT_DEFINED",
    )

    print_result(
        "Recommendation Boundary",
        registry[
            "recommendation_status"
        ] == "NOT_PROVIDED",
    )

    print()
    print("=" * 76)
    print(
        "SPRINT 0.9.6 PORTFOLIO HEALTH "
        "CONTEXT REQUIREMENTS TEST: PASS"
    )
    print("=" * 76)


if __name__ == "__main__":
    main()
