class PortfolioHealthSeverityService:
    """
    Deterministic portfolio-health diagnostic severity service.

    Converts supported descriptive diagnostic classifications into
    a separate severity-classification layer.

    Important boundaries:
    - Severity is separate from factual observations.
    - Severity is separate from descriptive classifications.
    - Severity applies only where an explicit deterministic rule exists.
    - Rule eligibility does not imply that a severity rule is defined.
    - Data sufficiency must be established before severity is produced.
    - Analysis applies only to imported and persisted holdings.
    - Portfolio completeness is not confirmed.
    - Severity does not represent complete-portfolio health.
    - Severity must not automatically trigger rebalancing or selling.
    - No portfolio-health score is produced.
    - No target allocation is defined.
    - No rebalance or investment recommendation is produced.
    """

    CLASSIFICATION_SCOPE = (
        "IMPORTED_PERSISTED_HOLDINGS"
    )

    RULE_REGISTRY = {
        "LARGEST_SECURITY_POSITION": {
            "rule_id": (
                "SEVERITY_LARGEST_SECURITY_POSITION"
            ),
            "classification": (
                "SECURITY_CONCENTRATION"
            ),
            "dimension": "SECURITY",
            "rule_status": "DEFERRED",
            "eligibility_status": (
                "INSUFFICIENT_CONTEXT"
            ),
            "data_requirement_status": (
                "INSTRUMENT_INTELLIGENCE_REQUIRED"
            ),
            "limitation": (
                "A persisted security position may represent a direct "
                "security, ETF, mutual fund, or another instrument type. "
                "Position weight alone is insufficient for severity "
                "classification without adequate instrument intelligence "
                "and exposure context."
            ),
        },
        "TOP_THREE_SECURITY_ALLOCATION": {
            "rule_id": (
                "SEVERITY_TOP_THREE_SECURITY_ALLOCATION"
            ),
            "classification": (
                "SECURITY_CONCENTRATION"
            ),
            "dimension": "SECURITY",
            "rule_status": "DEFERRED",
            "eligibility_status": (
                "INSUFFICIENT_CONTEXT"
            ),
            "data_requirement_status": (
                "INSTRUMENT_INTELLIGENCE_REQUIRED"
            ),
            "limitation": (
                "Top-three persisted security allocation does not by "
                "itself establish underlying investment concentration. "
                "ETF and mutual-fund positions may contain diversified "
                "underlying exposures that are not yet modeled."
            ),
        },
        "LARGEST_ACCOUNT_ALLOCATION": {
            "rule_id": (
                "SEVERITY_LARGEST_ACCOUNT_ALLOCATION"
            ),
            "classification": (
                "ACCOUNT_CONCENTRATION"
            ),
            "dimension": "ACCOUNT",
            "rule_status": "DEFERRED",
            "eligibility_status": (
                "INSUFFICIENT_RISK_SEMANTICS"
            ),
            "data_requirement_status": (
                "ACCOUNT_RISK_MODEL_REQUIRED"
            ),
            "limitation": (
                "Account allocation concentration is a factual custody "
                "or account-distribution observation. A high account "
                "weight does not automatically establish investment-risk "
                "severity without a separately defined account-risk model."
            ),
        },
        "LARGEST_ASSET_TYPE_ALLOCATION": {
            "rule_id": (
                "SEVERITY_LARGEST_ASSET_TYPE_ALLOCATION"
            ),
            "classification": (
                "ASSET_TYPE_CONCENTRATION"
            ),
            "dimension": "ASSET_TYPE",
            "rule_status": "DEFERRED",
            "eligibility_status": (
                "INSUFFICIENT_CONTEXT"
            ),
            "data_requirement_status": (
                "UNDERLYING_EXPOSURE_MODEL_REQUIRED"
            ),
            "limitation": (
                "Persisted asset-type labels alone do not establish "
                "economic diversification or concentration severity. "
                "Underlying ETF and mutual-fund exposures are not yet "
                "available."
            ),
        },
    }

    def get_rule_registry(self):
        """
        Return deterministic severity-rule eligibility metadata.

        Registry membership identifies diagnostic classifications that
        may support future severity rules. Each candidate remains gated
        by explicit data-sufficiency and semantic requirements.

        Registry membership must not itself produce severity.
        """

        rules = []

        for observation_code, rule in (
            self.RULE_REGISTRY.items()
        ):

            rules.append(
                {
                    "observation_code": (
                        observation_code
                    ),
                    "rule_id": (
                        rule[
                            "rule_id"
                        ]
                    ),
                    "classification": (
                        rule[
                            "classification"
                        ]
                    ),
                    "dimension": (
                        rule[
                            "dimension"
                        ]
                    ),
                    "rule_status": (
                        rule[
                            "rule_status"
                        ]
                    ),
                    "eligibility_status": (
                        rule[
                            "eligibility_status"
                        ]
                    ),
                    "data_requirement_status": (
                        rule[
                            "data_requirement_status"
                        ]
                    ),
                    "limitation": (
                        rule[
                            "limitation"
                        ]
                    ),
                    "severity_scope": (
                        self.CLASSIFICATION_SCOPE
                    ),
                    "provenance": (
                        "SEVERITY_RULE_REGISTRY"
                    ),
                }
            )

        return {
            "rules": rules,
            "rule_count": len(
                rules
            ),
            "eligible_rule_count": sum(
                1
                for rule in rules
                if rule[
                    "eligibility_status"
                ] == "ELIGIBLE"
            ),
            "registry_status": (
                "RULES_REGISTERED_ELIGIBILITY_GATED"
            ),
            "severity_scope": (
                self.CLASSIFICATION_SCOPE
            ),
            "portfolio_completeness": (
                "NOT_CONFIRMED"
            ),
        }

    def evaluate_rule_context_eligibility(
        self,
        context_availability,
    ):
        """
        Evaluate severity-rule context eligibility from an explicit
        context-availability contract.

        Context sufficiency may remove a data-sufficiency blocker,
        but it does not define or execute a severity rule.

        A context-eligible rule therefore remains DEFERRED until an
        explicit deterministic severity rule is separately defined
        and tested.
        """

        evaluations = (
            context_availability.get(
                "evaluations",
                [],
            )
            if context_availability
            else []
        )

        availability_map = {
            evaluation[
                "data_requirement_status"
            ]: evaluation
            for evaluation in evaluations
        }

        rule_evaluations = []

        for observation_code, rule in (
            self.RULE_REGISTRY.items()
        ):

            data_requirement_status = (
                rule[
                    "data_requirement_status"
                ]
            )

            context_evaluation = (
                availability_map.get(
                    data_requirement_status
                )
            )

            context_available = (
                context_evaluation is not None
                and context_evaluation[
                    "requirement_available"
                ] is True
            )

            rule_evaluations.append(
                {
                    "observation_code": (
                        observation_code
                    ),
                    "rule_id": (
                        rule[
                            "rule_id"
                        ]
                    ),
                    "classification": (
                        rule[
                            "classification"
                        ]
                    ),
                    "dimension": (
                        rule[
                            "dimension"
                        ]
                    ),
                    "data_requirement_status": (
                        data_requirement_status
                    ),
                    "context_available": (
                        context_available
                    ),
                    "context_eligibility_status": (
                        "CONTEXT_ELIGIBLE"
                        if context_available
                        else "CONTEXT_INELIGIBLE"
                    ),
                    "severity_rule_status": (
                        "DEFERRED"
                    ),
                    "severity_rule_defined": (
                        False
                    ),
                    "severity_output_eligible": (
                        False
                    ),
                    "severity_scope": (
                        self.CLASSIFICATION_SCOPE
                    ),
                    "provenance": (
                        "SEVERITY_CONTEXT_"
                        "ELIGIBILITY_EVALUATION"
                    ),
                }
            )

        context_eligible_rule_count = sum(
            1
            for evaluation
            in rule_evaluations
            if evaluation[
                "context_available"
            ]
        )

        return {
            "rule_evaluations": (
                rule_evaluations
            ),
            "rule_count": len(
                rule_evaluations
            ),
            "context_eligible_rule_count": (
                context_eligible_rule_count
            ),
            "context_ineligible_rule_count": (
                len(
                    rule_evaluations
                )
                - context_eligible_rule_count
            ),
            "severity_output_eligible_rule_count": (
                0
            ),
            "eligibility_status": (
                "CONTEXT_REQUIREMENTS_SATISFIED"
                if (
                    rule_evaluations
                    and context_eligible_rule_count
                    == len(
                        rule_evaluations
                    )
                )
                else "CONTEXT_REQUIREMENTS_INCOMPLETE"
            ),
            "severity_rule_status": (
                "RULES_NOT_DEFINED"
            ),
            "severity_scope": (
                self.CLASSIFICATION_SCOPE
            ),
            "portfolio_completeness": (
                "NOT_CONFIRMED"
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

    def classify_severity(
        self,
        classifications,
    ):
        """
        Return the severity-classification contract.

        No severity may be produced unless an eligible explicit
        deterministic severity rule exists and is separately tested.
        """

        severity_classifications = []

        return {
            "severity_classifications": (
                severity_classifications
            ),
            "severity_classification_count": (
                len(
                    severity_classifications
                )
            ),
            "severity_status": (
                "ELIGIBILITY_GATED"
            ),
            "severity_scope": (
                self.CLASSIFICATION_SCOPE
            ),
            "portfolio_completeness": (
                "NOT_CONFIRMED"
            ),
            "severity_rule_status": (
                "NO_ELIGIBLE_RULES"
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
