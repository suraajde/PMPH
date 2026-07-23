from services.portfolio_health_classification_service import (
    PortfolioHealthClassificationService,
)


def main():

    print("=" * 76)
    print(
        "PMPH PORTFOLIO HEALTH CLASSIFICATION SERVICE TEST"
    )
    print("=" * 76)

    service = (
        PortfolioHealthClassificationService()
    )

    # =====================================================
    # EMPTY CLASSIFICATION CONTRACT
    # =====================================================

    empty_result = (
        service.classify_observations(
            []
        )
    )

    empty_pass = (
        empty_result[
            "classifications"
        ] == []
        and empty_result[
            "classification_count"
        ] == 0
    )

    empty_boundary_pass = (
        empty_result[
            "classification_status"
        ]
        == "DESCRIPTIVE_ONLY"
        and empty_result[
            "classification_scope"
        ]
        == "IMPORTED_PERSISTED_HOLDINGS"
        and empty_result[
            "portfolio_completeness"
        ]
        == "NOT_CONFIRMED"
    )

    # =====================================================
    # SUPPORTED OBSERVATIONS
    # =====================================================

    observations = [
        {
            "code": (
                "LARGEST_SECURITY_POSITION"
            ),
            "dimension": "SECURITY",
            "observed_value": 40.0,
        },
        {
            "code": (
                "TOP_THREE_SECURITY_ALLOCATION"
            ),
            "dimension": "SECURITY",
            "observed_value": 90.0,
        },
        {
            "code": (
                "LARGEST_ACCOUNT_ALLOCATION"
            ),
            "dimension": "ACCOUNT",
            "observed_value": 70.0,
        },
        {
            "code": (
                "LARGEST_ASSET_TYPE_ALLOCATION"
            ),
            "dimension": "ASSET_TYPE",
            "observed_value": 60.0,
        },
    ]

    result = (
        service.classify_observations(
            observations
        )
    )

    classifications = result[
        "classifications"
    ]

    # =====================================================
    # CLASSIFICATION MAPPING
    # =====================================================

    mapping = {
        item["observation_code"]:
        item["classification"]
        for item in classifications
    }

    mapping_pass = (
        result[
            "classification_count"
        ] == 4
        and mapping
        == {
            "LARGEST_SECURITY_POSITION": (
                "SECURITY_CONCENTRATION"
            ),
            "TOP_THREE_SECURITY_ALLOCATION": (
                "SECURITY_CONCENTRATION"
            ),
            "LARGEST_ACCOUNT_ALLOCATION": (
                "ACCOUNT_CONCENTRATION"
            ),
            "LARGEST_ASSET_TYPE_ALLOCATION": (
                "ASSET_TYPE_CONCENTRATION"
            ),
        }
    )

    # =====================================================
    # DIMENSION CONTRACT
    # =====================================================

    dimensions = {
        item["observation_code"]:
        item[
            "classification_dimension"
        ]
        for item in classifications
    }

    dimension_pass = (
        dimensions
        == {
            "LARGEST_SECURITY_POSITION": (
                "SECURITY"
            ),
            "TOP_THREE_SECURITY_ALLOCATION": (
                "SECURITY"
            ),
            "LARGEST_ACCOUNT_ALLOCATION": (
                "ACCOUNT"
            ),
            "LARGEST_ASSET_TYPE_ALLOCATION": (
                "ASSET_TYPE"
            ),
        }
    )

    # =====================================================
    # OBSERVED VALUE PRESERVATION
    # =====================================================

    observed_values = {
        item["observation_code"]:
        item["observed_value"]
        for item in classifications
    }

    observed_value_pass = (
        observed_values
        == {
            "LARGEST_SECURITY_POSITION": 40.0,
            "TOP_THREE_SECURITY_ALLOCATION": 90.0,
            "LARGEST_ACCOUNT_ALLOCATION": 70.0,
            "LARGEST_ASSET_TYPE_ALLOCATION": 60.0,
        }
    )

    # =====================================================
    # CLASSIFICATION PROVENANCE
    # =====================================================

    provenance_pass = all(
        item[
            "classification_type"
        ]
        == "DESCRIPTIVE"
        and item[
            "classification_scope"
        ]
        == "IMPORTED_PERSISTED_HOLDINGS"
        and item[
            "provenance"
        ]
        == "DETERMINISTIC_DIAGNOSTIC_RULE"
        for item in classifications
    )

    # =====================================================
    # UNKNOWN OBSERVATION SAFETY
    # =====================================================

    unknown_result = (
        service.classify_observations(
            [
                {
                    "code": (
                        "UNKNOWN_DIAGNOSTIC"
                    ),
                    "observed_value": 99.0,
                }
            ]
        )
    )

    unknown_pass = (
        unknown_result[
            "classifications"
        ] == []
        and unknown_result[
            "classification_count"
        ] == 0
    )

    # =====================================================
    # SCOPE AND SAFETY BOUNDARIES
    # =====================================================

    scope_pass = (
        result[
            "classification_status"
        ]
        == "DESCRIPTIVE_ONLY"
        and result[
            "classification_scope"
        ]
        == "IMPORTED_PERSISTED_HOLDINGS"
        and result[
            "portfolio_completeness"
        ]
        == "NOT_CONFIRMED"
    )

    scoring_boundary_pass = (
        result[
            "severity_classification"
        ]
        == "NOT_DEFINED"
        and result[
            "health_score"
        ]
        == "NOT_AVAILABLE"
        and result[
            "target_allocation"
        ]
        == "NOT_DEFINED"
        and result[
            "recommendation_status"
        ]
        == "NOT_PROVIDED"
    )

    print()
    print("-" * 76)

    checks = [
        (
            "Empty Classification Contract",
            empty_pass,
        ),
        (
            "Empty Classification Boundary",
            empty_boundary_pass,
        ),
        (
            "Deterministic Classification Mapping",
            mapping_pass,
        ),
        (
            "Classification Dimensions",
            dimension_pass,
        ),
        (
            "Observed Value Preservation",
            observed_value_pass,
        ),
        (
            "Classification Scope and Provenance",
            provenance_pass,
        ),
        (
            "Unknown Observation Safety",
            unknown_pass,
        ),
        (
            "Imported Portfolio Scope",
            scope_pass,
        ),
        (
            "Scoring and Recommendation Boundary",
            scoring_boundary_pass,
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
            "Portfolio Health Classification Service test failed."
        )

    print(
        "SPRINT 0.9.4 PORTFOLIO HEALTH "
        "CLASSIFICATION SERVICE TEST: PASS"
    )

    print("=" * 76)


if __name__ == "__main__":

    main()
