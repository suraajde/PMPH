from services.portfolio_health_severity_service import (
    PortfolioHealthSeverityService,
)


def assert_equal(
    actual,
    expected,
    label,
):
    if actual != expected:
        raise AssertionError(
            f"{label}: expected {expected!r}, "
            f"got {actual!r}"
        )

    print(
        f"{label}: PASS"
    )


def assert_true(
    condition,
    label,
):
    if not condition:
        raise AssertionError(
            f"{label}: condition was not true"
        )

    print(
        f"{label}: PASS"
    )


def main():

    print()
    print(
        "=" * 76
    )
    print(
        "PMPH PORTFOLIO HEALTH SEVERITY SERVICE TEST"
    )
    print(
        "=" * 76
    )

    service = (
        PortfolioHealthSeverityService()
    )

    # =====================================================
    # EMPTY SEVERITY CONTRACT
    # =====================================================

    empty_result = (
        service.classify_severity(
            []
        )
    )

    assert_equal(
        empty_result[
            "severity_classifications"
        ],
        [],
        "Empty Severity Contract",
    )

    assert_equal(
        empty_result[
            "severity_classification_count"
        ],
        0,
        "Empty Severity Count",
    )

    # =====================================================
    # EXPLICIT ELIGIBILITY GATE
    # =====================================================

    assert_equal(
        empty_result[
            "severity_status"
        ],
        "ELIGIBILITY_GATED",
        "Severity Eligibility Gate",
    )

    assert_equal(
        empty_result[
            "severity_rule_status"
        ],
        "NO_ELIGIBLE_RULES",
        "No Eligible Severity Rules",
    )

    # =====================================================
    # RULE REGISTRY
    # =====================================================

    registry = (
        service.get_rule_registry()
    )

    assert_equal(
        registry[
            "rule_count"
        ],
        4,
        "Severity Rule Registry Count",
    )

    assert_equal(
        registry[
            "eligible_rule_count"
        ],
        0,
        "Eligible Severity Rule Count",
    )

    assert_equal(
        registry[
            "registry_status"
        ],
        (
            "RULES_REGISTERED_"
            "ELIGIBILITY_GATED"
        ),
        "Severity Registry Status",
    )

    # =====================================================
    # REGISTERED OBSERVATION CODES
    # =====================================================

    rules_by_code = {
        rule[
            "observation_code"
        ]: rule
        for rule in registry[
            "rules"
        ]
    }

    expected_codes = {
        "LARGEST_SECURITY_POSITION",
        "TOP_THREE_SECURITY_ALLOCATION",
        "LARGEST_ACCOUNT_ALLOCATION",
        "LARGEST_ASSET_TYPE_ALLOCATION",
    }

    assert_equal(
        set(
            rules_by_code.keys()
        ),
        expected_codes,
        "Registered Severity Candidates",
    )

    # =====================================================
    # SECURITY CONCENTRATION GATES
    # =====================================================

    largest_security = (
        rules_by_code[
            "LARGEST_SECURITY_POSITION"
        ]
    )

    assert_equal(
        largest_security[
            "rule_status"
        ],
        "DEFERRED",
        "Largest Security Rule Deferred",
    )

    assert_equal(
        largest_security[
            "eligibility_status"
        ],
        "INSUFFICIENT_CONTEXT",
        "Largest Security Eligibility Gate",
    )

    assert_equal(
        largest_security[
            "data_requirement_status"
        ],
        (
            "INSTRUMENT_INTELLIGENCE_"
            "REQUIRED"
        ),
        "Largest Security Data Requirement",
    )

    top_three = (
        rules_by_code[
            "TOP_THREE_SECURITY_ALLOCATION"
        ]
    )

    assert_equal(
        top_three[
            "rule_status"
        ],
        "DEFERRED",
        "Top Three Rule Deferred",
    )

    assert_equal(
        top_three[
            "data_requirement_status"
        ],
        (
            "INSTRUMENT_INTELLIGENCE_"
            "REQUIRED"
        ),
        "Top Three Data Requirement",
    )

    # =====================================================
    # ACCOUNT CONCENTRATION GATE
    # =====================================================

    account_rule = (
        rules_by_code[
            "LARGEST_ACCOUNT_ALLOCATION"
        ]
    )

    assert_equal(
        account_rule[
            "eligibility_status"
        ],
        (
            "INSUFFICIENT_RISK_SEMANTICS"
        ),
        "Account Severity Semantic Gate",
    )

    assert_equal(
        account_rule[
            "data_requirement_status"
        ],
        "ACCOUNT_RISK_MODEL_REQUIRED",
        "Account Risk Model Requirement",
    )

    # =====================================================
    # ASSET TYPE CONCENTRATION GATE
    # =====================================================

    asset_type_rule = (
        rules_by_code[
            "LARGEST_ASSET_TYPE_ALLOCATION"
        ]
    )

    assert_equal(
        asset_type_rule[
            "eligibility_status"
        ],
        "INSUFFICIENT_CONTEXT",
        "Asset Type Eligibility Gate",
    )

    assert_equal(
        asset_type_rule[
            "data_requirement_status"
        ],
        (
            "UNDERLYING_EXPOSURE_MODEL_"
            "REQUIRED"
        ),
        "Underlying Exposure Requirement",
    )

    # =====================================================
    # LIMITATION / PROVENANCE CONTRACT
    # =====================================================

    for rule in registry[
        "rules"
    ]:

        assert_true(
            bool(
                rule[
                    "limitation"
                ].strip()
            ),
            (
                "Explicit Limitation - "
                + rule[
                    "observation_code"
                ]
            ),
        )

        assert_equal(
            rule[
                "provenance"
            ],
            "SEVERITY_RULE_REGISTRY",
            (
                "Severity Provenance - "
                + rule[
                    "observation_code"
                ]
            ),
        )

        assert_equal(
            rule[
                "severity_scope"
            ],
            (
                "IMPORTED_PERSISTED_"
                "HOLDINGS"
            ),
            (
                "Severity Scope - "
                + rule[
                    "observation_code"
                ]
            ),
        )

    # =====================================================
    # NO PREMATURE SEVERITY
    # =====================================================

    sample_classifications = [
        {
            "observation_code": (
                "LARGEST_SECURITY_POSITION"
            ),
            "classification": (
                "SECURITY_CONCENTRATION"
            ),
            "observed_value": 53.48,
        },
        {
            "observation_code": (
                "TOP_THREE_SECURITY_ALLOCATION"
            ),
            "classification": (
                "SECURITY_CONCENTRATION"
            ),
            "observed_value": 95.27,
        },
        {
            "observation_code": (
                "LARGEST_ACCOUNT_ALLOCATION"
            ),
            "classification": (
                "ACCOUNT_CONCENTRATION"
            ),
            "observed_value": 88.37,
        },
        {
            "observation_code": (
                "LARGEST_ASSET_TYPE_ALLOCATION"
            ),
            "classification": (
                "ASSET_TYPE_CONCENTRATION"
            ),
            "observed_value": 100.0,
        },
    ]

    result = (
        service.classify_severity(
            sample_classifications
        )
    )

    assert_equal(
        result[
            "severity_classifications"
        ],
        [],
        "No Premature Severity Output",
    )

    assert_equal(
        result[
            "severity_classification_count"
        ],
        0,
        "No Premature Severity Count",
    )

    # =====================================================
    # IMPORTED PORTFOLIO SCOPE
    # =====================================================

    assert_equal(
        result[
            "severity_scope"
        ],
        (
            "IMPORTED_PERSISTED_"
            "HOLDINGS"
        ),
        "Imported Portfolio Scope",
    )

    assert_equal(
        result[
            "portfolio_completeness"
        ],
        "NOT_CONFIRMED",
        "Portfolio Completeness Boundary",
    )

    # =====================================================
    # SCORING / RECOMMENDATION BOUNDARY
    # =====================================================

    assert_equal(
        result[
            "health_score"
        ],
        "NOT_AVAILABLE",
        "Health Score Boundary",
    )

    assert_equal(
        result[
            "target_allocation"
        ],
        "NOT_DEFINED",
        "Target Allocation Boundary",
    )

    assert_equal(
        result[
            "recommendation_status"
        ],
        "NOT_PROVIDED",
        "Recommendation Boundary",
    )

    print()
    print(
        "=" * 76
    )
    print(
        "SPRINT 0.9.5 PORTFOLIO HEALTH "
        "SEVERITY ELIGIBILITY TEST: PASS"
    )
    print(
        "=" * 76
    )


if __name__ == "__main__":
    main()
