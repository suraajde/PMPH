class PortfolioHealthInstrumentIntelligenceService:
    """
    Deterministic portfolio-health instrument intelligence foundation.

    Interprets explicitly persisted instrument metadata without
    inventing unsupported market or underlying-exposure information.

    Important boundaries:
    - Persisted instrument metadata is treated as imported evidence.
    - Instrument identity is separate from instrument classification.
    - Investment structure is derived only from explicitly supported
      persisted asset-type semantics.
    - Unknown or unsupported asset types remain UNKNOWN.
    - No underlying holdings are inferred.
    - No economic exposure is inferred.
    - No diversification or overlap is inferred.
    - No severity is assigned.
    - No portfolio-health score is produced.
    - No target allocation is defined.
    - No rebalance or investment recommendation is produced.
    """

    CONTEXT_SCOPE = (
        "IMPORTED_PERSISTED_HOLDINGS"
    )

    SUPPORTED_ASSET_TYPES = {
        "ETF": {
            "instrument_classification": "ETF",
            "investment_structure": (
                "POOLED_INVESTMENT_VEHICLE"
            ),
        },
        "MUTUAL_FUND": {
            "instrument_classification": (
                "MUTUAL_FUND"
            ),
            "investment_structure": (
                "POOLED_INVESTMENT_VEHICLE"
            ),
        },
        "EQUITY": {
            "instrument_classification": (
                "DIRECT_EQUITY"
            ),
            "investment_structure": (
                "DIRECT_SECURITY"
            ),
        },
        "STOCK": {
            "instrument_classification": (
                "DIRECT_EQUITY"
            ),
            "investment_structure": (
                "DIRECT_SECURITY"
            ),
        },
    }

    def evaluate_portfolio_instruments(
        self,
        holdings,
    ):
        """
        Evaluate instrument intelligence across persisted holdings.

        Portfolio-level capabilities are exposed only when every
        evaluated holding satisfies the corresponding capability.

        Empty portfolios do not establish instrument intelligence.
        """

        holdings = list(
            holdings or []
        )

        instrument_evaluations = [
            self.classify_instrument(
                holding
            )
            for holding in holdings
        ]

        required_capabilities = [
            "INSTRUMENT_IDENTITY",
            "INSTRUMENT_CLASSIFICATION",
            "INVESTMENT_STRUCTURE",
        ]

        available_capabilities = []

        if instrument_evaluations:

            for capability in required_capabilities:

                if all(
                    capability
                    in evaluation[
                        "available_capabilities"
                    ]
                    for evaluation
                    in instrument_evaluations
                ):

                    available_capabilities.append(
                        capability
                    )

        missing_capabilities = [
            capability
            for capability
            in required_capabilities
            if capability
            not in available_capabilities
        ]

        fully_intelligent_count = sum(
            1
            for evaluation
            in instrument_evaluations
            if evaluation[
                "instrument_intelligence_available"
            ]
        )

        incomplete_instruments = [
            {
                "security_key": evaluation[
                    "security_key"
                ],
                "symbol": evaluation[
                    "symbol"
                ],
                "persisted_asset_type": evaluation[
                    "persisted_asset_type"
                ],
                "missing_capabilities": list(
                    evaluation[
                        "missing_capabilities"
                    ]
                ),
            }
            for evaluation
            in instrument_evaluations
            if not evaluation[
                "instrument_intelligence_available"
            ]
        ]

        portfolio_instrument_intelligence_available = (
            bool(
                instrument_evaluations
            )
            and fully_intelligent_count
            == len(
                instrument_evaluations
            )
            and len(
                missing_capabilities
            ) == 0
        )

        return {
            "instrument_evaluations": (
                instrument_evaluations
            ),
            "instrument_count": len(
                instrument_evaluations
            ),
            "fully_intelligent_instrument_count": (
                fully_intelligent_count
            ),
            "incomplete_instrument_count": (
                len(
                    instrument_evaluations
                )
                - fully_intelligent_count
            ),
            "available_capabilities": (
                available_capabilities
            ),
            "missing_capabilities": (
                missing_capabilities
            ),
            "portfolio_instrument_intelligence_available": (
                portfolio_instrument_intelligence_available
            ),
            "incomplete_instruments": (
                incomplete_instruments
            ),
            "context_scope": (
                self.CONTEXT_SCOPE
            ),
            "portfolio_completeness": (
                "NOT_CONFIRMED"
            ),
            "underlying_exposure_status": (
                "NOT_AVAILABLE"
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

    @staticmethod
    def _get_holding_value(
        holding,
        field_name,
    ):
        """
        Read one persisted holding field from either a mapping-style
        input or a StoredHolding-style object.

        Instrument intelligence owns this compatibility boundary so
        callers do not need to convert persisted domain models into
        ad-hoc dictionaries.
        """

        if isinstance(
            holding,
            dict,
        ):

            return holding.get(
                field_name
            )

        value = getattr(
            holding,
            field_name,
            None,
        )

        if callable(
            value
        ):

            return value()

        return value

    def classify_instrument(
        self,
        holding,
    ):
        """
        Return deterministic instrument intelligence derived only
        from explicitly persisted holding metadata.
        """

        holding = holding or {}

        security_key = (
            self._get_holding_value(
                holding,
                "security_key",
            )
            or ""
        )

        symbol = (
            self._get_holding_value(
                holding,
                "symbol",
            )
            or ""
        )

        name = (
            self._get_holding_value(
                holding,
                "name",
            )
            or ""
        )

        isin = (
            self._get_holding_value(
                holding,
                "isin",
            )
            or ""
        )

        asset_type = (
            self._get_holding_value(
                holding,
                "asset_type",
            )
            or ""
        )

        asset_type = (
            str(
                asset_type
            )
            .strip()
            .upper()
        )

        identity_available = any(
            [
                bool(
                    str(
                        security_key
                    ).strip()
                ),
                bool(
                    str(
                        symbol
                    ).strip()
                ),
                bool(
                    str(
                        isin
                    ).strip()
                ),
            ]
        )

        classification_definition = (
            self.SUPPORTED_ASSET_TYPES.get(
                asset_type
            )
        )

        classification_available = (
            classification_definition
            is not None
        )

        if classification_available:

            instrument_classification = (
                classification_definition[
                    "instrument_classification"
                ]
            )

            investment_structure = (
                classification_definition[
                    "investment_structure"
                ]
            )

        else:

            instrument_classification = (
                "UNKNOWN"
            )

            investment_structure = (
                "UNKNOWN"
            )

        investment_structure_available = (
            investment_structure
            != "UNKNOWN"
        )

        available_capabilities = []

        if identity_available:

            available_capabilities.append(
                "INSTRUMENT_IDENTITY"
            )

        if classification_available:

            available_capabilities.append(
                "INSTRUMENT_CLASSIFICATION"
            )

        if investment_structure_available:

            available_capabilities.append(
                "INVESTMENT_STRUCTURE"
            )

        required_capabilities = [
            "INSTRUMENT_IDENTITY",
            "INSTRUMENT_CLASSIFICATION",
            "INVESTMENT_STRUCTURE",
        ]

        missing_capabilities = [
            capability
            for capability
            in required_capabilities
            if capability
            not in available_capabilities
        ]

        intelligence_available = (
            len(
                missing_capabilities
            ) == 0
        )

        return {
            "security_key": security_key,
            "symbol": symbol,
            "name": name,
            "isin": isin,
            "persisted_asset_type": (
                asset_type
                if asset_type
                else "UNKNOWN"
            ),
            "instrument_classification": (
                instrument_classification
            ),
            "investment_structure": (
                investment_structure
            ),
            "identity_available": (
                identity_available
            ),
            "classification_available": (
                classification_available
            ),
            "investment_structure_available": (
                investment_structure_available
            ),
            "available_capabilities": (
                available_capabilities
            ),
            "missing_capabilities": (
                missing_capabilities
            ),
            "instrument_intelligence_available": (
                intelligence_available
            ),
            "context_scope": (
                self.CONTEXT_SCOPE
            ),
            "provenance": (
                "PERSISTED_HOLDING_METADATA"
            ),
            "underlying_exposure_status": (
                "NOT_AVAILABLE"
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
