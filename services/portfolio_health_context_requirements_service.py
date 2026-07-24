class PortfolioHealthContextRequirementsService:
    """
    Defines deterministic context requirements that must be satisfied
    before portfolio-health diagnostic severity can be evaluated.

    This service does not provide instrument intelligence itself.
    It defines what supporting context is required.

    Important boundaries:
    - Context requirements are separate from factual observations.
    - Context requirements are separate from descriptive classifications.
    - Context requirements do not assign severity.
    - Missing context must not be interpreted as portfolio risk.
    - Portfolio completeness is not confirmed.
    - No portfolio-health score is produced.
    - No target allocation is imposed.
    - No rebalance or investment recommendation is produced.
    """

    CONTEXT_SCOPE = (
        "IMPORTED_PERSISTED_HOLDINGS"
    )

    REQUIREMENT_REGISTRY = {
        "INSTRUMENT_INTELLIGENCE_REQUIRED": {
            "requirement_id": (
                "PORTFOLIO_HEALTH_INSTRUMENT_INTELLIGENCE"
            ),
            "requirement_type": (
                "INSTRUMENT_CONTEXT"
            ),
            "required_capabilities": [
                "INSTRUMENT_IDENTITY",
                "INSTRUMENT_CLASSIFICATION",
                "INVESTMENT_STRUCTURE",
            ],
            "requirement_status": (
                "NOT_AVAILABLE"
            ),
            "purpose": (
                "Distinguish direct securities, ETFs, mutual funds, "
                "and other investment structures before interpreting "
                "position concentration."
            ),
        },
        "UNDERLYING_EXPOSURE_MODEL_REQUIRED": {
            "requirement_id": (
                "PORTFOLIO_HEALTH_UNDERLYING_EXPOSURE"
            ),
            "requirement_type": (
                "EXPOSURE_CONTEXT"
            ),
            "required_capabilities": [
                "UNDERLYING_HOLDINGS",
                "ECONOMIC_EXPOSURE",
                "DIVERSIFICATION_CONTEXT",
                "OVERLAP_CONTEXT",
            ],
            "requirement_status": (
                "NOT_AVAILABLE"
            ),
            "purpose": (
                "Understand underlying ETF and mutual-fund exposures "
                "before interpreting economic diversification or "
                "concentration."
            ),
        },
        "ACCOUNT_RISK_MODEL_REQUIRED": {
            "requirement_id": (
                "PORTFOLIO_HEALTH_ACCOUNT_RISK_SEMANTICS"
            ),
            "requirement_type": (
                "ACCOUNT_CONTEXT"
            ),
            "required_capabilities": [
                "ACCOUNT_ROLE",
                "ACCOUNT_RISK_SEMANTICS",
            ],
            "requirement_status": (
                "NOT_AVAILABLE"
            ),
            "purpose": (
                "Separate custody or account-distribution concentration "
                "from actual investment-risk concentration."
            ),
        },
    }

    def get_requirement_registry(self):
        """
        Return the deterministic portfolio-health context-requirement
        registry.
        """

        requirements = []

        for (
            data_requirement_status,
            requirement,
        ) in self.REQUIREMENT_REGISTRY.items():

            requirements.append(
                {
                    "data_requirement_status": (
                        data_requirement_status
                    ),
                    "requirement_id": (
                        requirement[
                            "requirement_id"
                        ]
                    ),
                    "requirement_type": (
                        requirement[
                            "requirement_type"
                        ]
                    ),
                    "required_capabilities": list(
                        requirement[
                            "required_capabilities"
                        ]
                    ),
                    "requirement_status": (
                        requirement[
                            "requirement_status"
                        ]
                    ),
                    "purpose": (
                        requirement[
                            "purpose"
                        ]
                    ),
                    "context_scope": (
                        self.CONTEXT_SCOPE
                    ),
                    "provenance": (
                        "PORTFOLIO_HEALTH_CONTEXT_REQUIREMENT_REGISTRY"
                    ),
                }
            )

        return {
            "requirements": requirements,
            "requirement_count": len(
                requirements
            ),
            "available_requirement_count": sum(
                1
                for requirement in requirements
                if requirement[
                    "requirement_status"
                ] == "AVAILABLE"
            ),
            "registry_status": (
                "CONTEXT_REQUIREMENTS_DEFINED"
            ),
            "context_scope": (
                self.CONTEXT_SCOPE
            ),
            "portfolio_completeness": (
                "NOT_CONFIRMED"
            ),
            "severity_status": (
                "NOT_EVALUATED"
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

    def evaluate_context_availability(
        self,
        available_capabilities=None,
    ):
        """
        Evaluate whether registered context requirements are
        satisfied by explicitly available capabilities.

        Capability availability must be supplied explicitly.
        Missing capabilities are never inferred as available.
        """

        if available_capabilities is None:
            available_capabilities = []

        available_capabilities = set(
            available_capabilities
        )

        evaluations = []

        for (
            data_requirement_status,
            requirement,
        ) in self.REQUIREMENT_REGISTRY.items():

            required_capabilities = (
                requirement[
                    "required_capabilities"
                ]
            )

            missing_capabilities = [
                capability
                for capability
                in required_capabilities
                if capability
                not in available_capabilities
            ]

            requirement_available = (
                len(
                    missing_capabilities
                ) == 0
            )

            evaluations.append(
                {
                    "data_requirement_status": (
                        data_requirement_status
                    ),
                    "requirement_id": (
                        requirement[
                            "requirement_id"
                        ]
                    ),
                    "requirement_type": (
                        requirement[
                            "requirement_type"
                        ]
                    ),
                    "required_capabilities": list(
                        required_capabilities
                    ),
                    "missing_capabilities": (
                        missing_capabilities
                    ),
                    "requirement_available": (
                        requirement_available
                    ),
                    "availability_status": (
                        "AVAILABLE"
                        if requirement_available
                        else "NOT_AVAILABLE"
                    ),
                    "context_scope": (
                        self.CONTEXT_SCOPE
                    ),
                    "provenance": (
                        "PORTFOLIO_HEALTH_"
                        "CONTEXT_AVAILABILITY_EVALUATION"
                    ),
                }
            )

        available_requirement_count = sum(
            1
            for evaluation
            in evaluations
            if evaluation[
                "requirement_available"
            ]
        )

        return {
            "evaluations": evaluations,
            "requirement_count": len(
                evaluations
            ),
            "available_requirement_count": (
                available_requirement_count
            ),
            "unavailable_requirement_count": (
                len(
                    evaluations
                )
                - available_requirement_count
            ),
            "availability_status": (
                "CONTEXT_AVAILABLE"
                if (
                    evaluations
                    and available_requirement_count
                    == len(
                        evaluations
                    )
                )
                else "CONTEXT_INCOMPLETE"
            ),
            "context_scope": (
                self.CONTEXT_SCOPE
            ),
            "portfolio_completeness": (
                "NOT_CONFIRMED"
            ),
            "severity_status": (
                "NOT_EVALUATED"
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

    def get_requirement(
        self,
        data_requirement_status,
    ):
        """
        Return one context requirement by the requirement status used
        by the severity eligibility registry.
        """

        requirement = (
            self.REQUIREMENT_REGISTRY.get(
                data_requirement_status
            )
        )

        if requirement is None:

            return None

        return {
            "data_requirement_status": (
                data_requirement_status
            ),
            "requirement_id": (
                requirement[
                    "requirement_id"
                ]
            ),
            "requirement_type": (
                requirement[
                    "requirement_type"
                ]
            ),
            "required_capabilities": list(
                requirement[
                    "required_capabilities"
                ]
            ),
            "requirement_status": (
                requirement[
                    "requirement_status"
                ]
            ),
            "purpose": (
                requirement[
                    "purpose"
                ]
            ),
            "context_scope": (
                self.CONTEXT_SCOPE
            ),
            "provenance": (
                "PORTFOLIO_HEALTH_CONTEXT_REQUIREMENT_REGISTRY"
            ),
        }
