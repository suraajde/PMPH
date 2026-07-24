from services.portfolio_analytics_service import (
    PortfolioAnalyticsService,
)
from services.portfolio_health_classification_service import (
    PortfolioHealthClassificationService,
)
from services.portfolio_health_severity_service import (
    PortfolioHealthSeverityService,
)


class PortfolioHealthService:
    """
    Read-only portfolio health diagnostic orchestration service.

    Consolidates deterministic persisted-data analytics into a
    structured portfolio-health diagnostic framework.

    Important boundaries:
    - Analysis applies only to imported and persisted holdings.
    - Portfolio completeness is not confirmed.
    - No health score is currently produced.
    - No target allocation is defined.
    - No overweight/underweight classification is produced.
    - No rebalance or investment recommendation is produced.
    - Underlying ETF/fund diversification is not available.
    - Fund/ETF overlap is not available.
    - Market-dependent analytics remain outside this phase.
    """

    def __init__(
        self,
        database_path="data/pmph_portfolio.db",
    ):

        self.database_path = database_path

        self.analytics_service = (
            PortfolioAnalyticsService(
                database_path=database_path,
            )
        )

        self.classification_service = (
            PortfolioHealthClassificationService()
        )

        self.severity_service = (
            PortfolioHealthSeverityService()
        )

    def get_health_diagnostics(self):
        """
        Return structured factual portfolio-health diagnostics
        using only currently supported persisted-data analytics.
        """

        concentration = (
            self.analytics_service
            .get_concentration_summary()
        )

        allocation = (
            self.analytics_service
            .get_allocation_diagnostics()
        )

        observations = []

        for diagnostic in allocation[
            "diagnostics"
        ]:

            observations.append(
                {
                    "code": diagnostic[
                        "code"
                    ],
                    "dimension": diagnostic[
                        "dimension"
                    ],
                    "observed_value": diagnostic[
                        "observed_value"
                    ],
                    "message": diagnostic[
                        "message"
                    ],
                    "source": (
                        "ALLOCATION_DIAGNOSTICS"
                    ),
                }
            )

        classification_result = (
            self.classification_service
            .classify_observations(
                observations
            )
        )

        severity_result = (
            self.severity_service
            .classify_severity(
                classification_result[
                    "classifications"
                ]
            )
        )

        return {
            "framework": (
                "PORTFOLIO_HEALTH_DIAGNOSTIC_FOUNDATION"
            ),
            "framework_status": (
                "OBSERVATION_ONLY"
            ),
            "portfolio_current_value": (
                allocation[
                    "portfolio_current_value"
                ]
            ),
            "security_count": (
                allocation[
                    "security_count"
                ]
            ),
            "account_count": (
                allocation[
                    "account_count"
                ]
            ),
            "asset_type_count": (
                allocation[
                    "asset_type_count"
                ]
            ),
            "observations": observations,
            "observation_count": len(
                observations
            ),
            "classifications": (
                classification_result[
                    "classifications"
                ]
            ),
            "classification_count": (
                classification_result[
                    "classification_count"
                ]
            ),
            "classification_status": (
                classification_result[
                    "classification_status"
                ]
            ),
            "classification_scope": (
                classification_result[
                    "classification_scope"
                ]
            ),
            "severity_classification": (
                classification_result[
                    "severity_classification"
                ]
            ),
            "severity_classifications": (
                severity_result[
                    "severity_classifications"
                ]
            ),
            "severity_classification_count": (
                severity_result[
                    "severity_classification_count"
                ]
            ),
            "severity_status": (
                severity_result[
                    "severity_status"
                ]
            ),
            "severity_scope": (
                severity_result[
                    "severity_scope"
                ]
            ),
            "severity_rule_status": (
                severity_result[
                    "severity_rule_status"
                ]
            ),
            "concentration_metrics": {
                "largest_position_percent": (
                    concentration[
                        "largest_position_percent"
                    ]
                ),
                "top_3_percent": (
                    concentration[
                        "top_3_percent"
                    ]
                ),
                "security_hhi": (
                    concentration[
                        "security_hhi"
                    ]
                ),
                "effective_security_positions": (
                    concentration[
                        "effective_security_positions"
                    ]
                ),
                "largest_account_percent": (
                    concentration[
                        "largest_account_percent"
                    ]
                ),
                "account_hhi": (
                    concentration[
                        "account_hhi"
                    ]
                ),
                "asset_type_hhi": (
                    concentration[
                        "asset_type_hhi"
                    ]
                ),
            },
            "analysis_scope": (
                allocation[
                    "allocation_scope"
                ]
            ),
            "portfolio_completeness": (
                allocation[
                    "portfolio_completeness"
                ]
            ),
            "scope_description": (
                allocation[
                    "scope_description"
                ]
            ),
            "complete_portfolio_analytics": (
                "NOT_AVAILABLE"
            ),
            "health_score": (
                "NOT_AVAILABLE"
            ),
            "target_allocation": (
                allocation[
                    "target_allocation"
                ]
            ),
            "recommendation_status": (
                allocation[
                    "recommendation_status"
                ]
            ),
            "underlying_diversification": (
                allocation[
                    "underlying_diversification"
                ]
            ),
            "fund_etf_overlap": (
                allocation[
                    "fund_etf_overlap"
                ]
            ),
            "market_dependent_analytics": (
                "NOT_AVAILABLE"
            ),
        }
