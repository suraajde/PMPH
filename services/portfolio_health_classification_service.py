class PortfolioHealthClassificationService:
    """
    Deterministic portfolio-health diagnostic classification service.

    Responsibilities:
    - Classify supported factual diagnostic observations.
    - Keep classification separate from factual observation generation.
    - Expose explicit classification scope and provenance.

    Important boundaries:
    - Classifications apply only to imported and persisted holdings.
    - Portfolio completeness is not confirmed.
    - Classifications are descriptive, not evaluative.
    - No LOW/MODERATE/HIGH severity is inferred.
    - No health score is produced.
    - No target allocation is defined.
    - No overweight/underweight conclusion is produced.
    - No rebalance or investment recommendation is produced.
    """

    CLASSIFICATION_RULES = {
        "LARGEST_SECURITY_POSITION": {
            "classification": (
                "SECURITY_CONCENTRATION"
            ),
            "classification_dimension": (
                "SECURITY"
            ),
        },
        "TOP_THREE_SECURITY_ALLOCATION": {
            "classification": (
                "SECURITY_CONCENTRATION"
            ),
            "classification_dimension": (
                "SECURITY"
            ),
        },
        "LARGEST_ACCOUNT_ALLOCATION": {
            "classification": (
                "ACCOUNT_CONCENTRATION"
            ),
            "classification_dimension": (
                "ACCOUNT"
            ),
        },
        "LARGEST_ASSET_TYPE_ALLOCATION": {
            "classification": (
                "ASSET_TYPE_CONCENTRATION"
            ),
            "classification_dimension": (
                "ASSET_TYPE"
            ),
        },
    }

    def classify_observations(
        self,
        observations,
    ):
        """
        Return deterministic descriptive classifications for
        supported factual diagnostic observations.

        Unsupported observations are not inferred or guessed.
        """

        classifications = []

        for observation in observations:

            code = observation.get(
                "code"
            )

            rule = self.CLASSIFICATION_RULES.get(
                code
            )

            if rule is None:
                continue

            classifications.append(
                {
                    "observation_code": code,
                    "classification": (
                        rule[
                            "classification"
                        ]
                    ),
                    "classification_dimension": (
                        rule[
                            "classification_dimension"
                        ]
                    ),
                    "observed_value": (
                        observation.get(
                            "observed_value"
                        )
                    ),
                    "classification_type": (
                        "DESCRIPTIVE"
                    ),
                    "classification_scope": (
                        "IMPORTED_PERSISTED_HOLDINGS"
                    ),
                    "provenance": (
                        "DETERMINISTIC_DIAGNOSTIC_RULE"
                    ),
                }
            )

        return {
            "classifications": classifications,
            "classification_count": len(
                classifications
            ),
            "classification_status": (
                "DESCRIPTIVE_ONLY"
            ),
            "classification_scope": (
                "IMPORTED_PERSISTED_HOLDINGS"
            ),
            "portfolio_completeness": (
                "NOT_CONFIRMED"
            ),
            "severity_classification": (
                "NOT_DEFINED"
            ),
            "health_score": (
                "NOT_AVAILABLE"
            ),
            "target_allocation": (
                "NOT_DEFINED"
            ),
            "recommendation_status": (
                "NOT_PROVIDED"
            ),
        }
