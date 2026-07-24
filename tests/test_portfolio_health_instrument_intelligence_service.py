from services.portfolio_health_instrument_intelligence_service import (
    PortfolioHealthInstrumentIntelligenceService,
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
        "PMPH PORTFOLIO HEALTH INSTRUMENT "
        "INTELLIGENCE SERVICE TEST"
    )
    print("=" * 76)

    service = (
        PortfolioHealthInstrumentIntelligenceService()
    )

    # =====================================================
    # ETF INSTRUMENT INTELLIGENCE
    # =====================================================

    etf = service.classify_instrument(
        {
            "security_key": "ISIN:INF179KC1FB2",
            "symbol": "HDFCSML250",
            "name": "HDFCSML250",
            "isin": "INF179KC1FB2",
            "asset_type": "ETF",
        }
    )

    print_result(
        "ETF Identity Available",
        etf[
            "identity_available"
        ] is True,
    )

    print_result(
        "ETF Classification",
        etf[
            "instrument_classification"
        ] == "ETF",
    )

    print_result(
        "ETF Investment Structure",
        etf[
            "investment_structure"
        ] == "POOLED_INVESTMENT_VEHICLE",
    )

    print_result(
        "ETF Required Capabilities",
        etf[
            "available_capabilities"
        ] == [
            "INSTRUMENT_IDENTITY",
            "INSTRUMENT_CLASSIFICATION",
            "INVESTMENT_STRUCTURE",
        ],
    )

    print_result(
        "ETF No Missing Capabilities",
        etf[
            "missing_capabilities"
        ] == [],
    )

    print_result(
        "ETF Instrument Intelligence Available",
        etf[
            "instrument_intelligence_available"
        ] is True,
    )

    # =====================================================
    # UNKNOWN ASSET TYPE SAFETY
    # =====================================================

    unknown = service.classify_instrument(
        {
            "security_key": "SYMBOL:UNKNOWN1",
            "symbol": "UNKNOWN1",
            "name": "Unknown Instrument",
            "isin": "",
            "asset_type": "UNSUPPORTED_TYPE",
        }
    )

    print_result(
        "Unknown Identity Preserved",
        unknown[
            "identity_available"
        ] is True,
    )

    print_result(
        "Unknown Classification Safe",
        unknown[
            "instrument_classification"
        ] == "UNKNOWN",
    )

    print_result(
        "Unknown Investment Structure Safe",
        unknown[
            "investment_structure"
        ] == "UNKNOWN",
    )

    print_result(
        "Unknown Classification Unavailable",
        unknown[
            "classification_available"
        ] is False,
    )

    print_result(
        "Unknown Structure Unavailable",
        unknown[
            "investment_structure_available"
        ] is False,
    )

    print_result(
        "Unknown Instrument Intelligence Gated",
        unknown[
            "instrument_intelligence_available"
        ] is False,
    )

    print_result(
        "Unknown Missing Capabilities",
        unknown[
            "missing_capabilities"
        ] == [
            "INSTRUMENT_CLASSIFICATION",
            "INVESTMENT_STRUCTURE",
        ],
    )

    # =====================================================
    # NO-IDENTITY BOUNDARY
    # =====================================================

    no_identity = service.classify_instrument(
        {
            "security_key": "",
            "symbol": "",
            "name": "Unnamed ETF",
            "isin": "",
            "asset_type": "ETF",
        }
    )

    print_result(
        "No Identity Boundary",
        no_identity[
            "identity_available"
        ] is False,
    )

    print_result(
        "ETF Classification Independent Of Identity",
        no_identity[
            "classification_available"
        ] is True
        and no_identity[
            "instrument_classification"
        ] == "ETF",
    )

    print_result(
        "ETF Structure Independent Of Identity",
        no_identity[
            "investment_structure_available"
        ] is True
        and no_identity[
            "investment_structure"
        ] == "POOLED_INVESTMENT_VEHICLE",
    )

    print_result(
        "No Identity Full Intelligence Gated",
        no_identity[
            "instrument_intelligence_available"
        ] is False,
    )

    print_result(
        "No Identity Missing Capability",
        no_identity[
            "missing_capabilities"
        ] == [
            "INSTRUMENT_IDENTITY",
        ],
    )

    # =====================================================
    # DIRECT EQUITY SEMANTICS
    # =====================================================

    equity = service.classify_instrument(
        {
            "security_key": "ISIN:INE000000001",
            "symbol": "TESTEQ",
            "name": "Test Equity",
            "isin": "INE000000001",
            "asset_type": "EQUITY",
        }
    )

    print_result(
        "Direct Equity Classification",
        equity[
            "instrument_classification"
        ] == "DIRECT_EQUITY",
    )

    print_result(
        "Direct Equity Structure",
        equity[
            "investment_structure"
        ] == "DIRECT_SECURITY",
    )

    print_result(
        "Direct Equity Intelligence Available",
        equity[
            "instrument_intelligence_available"
        ] is True,
    )

    # =====================================================
    # MUTUAL FUND SEMANTICS
    # =====================================================

    mutual_fund = service.classify_instrument(
        {
            "security_key": "ISIN:INF000000001",
            "symbol": "",
            "name": "Test Mutual Fund",
            "isin": "INF000000001",
            "asset_type": "MUTUAL_FUND",
        }
    )

    print_result(
        "Mutual Fund Classification",
        mutual_fund[
            "instrument_classification"
        ] == "MUTUAL_FUND",
    )

    print_result(
        "Mutual Fund Structure",
        mutual_fund[
            "investment_structure"
        ] == "POOLED_INVESTMENT_VEHICLE",
    )

    print_result(
        "Mutual Fund Intelligence Available",
        mutual_fund[
            "instrument_intelligence_available"
        ] is True,
    )

    # =====================================================
    # EMPTY HOLDING SAFETY
    # =====================================================

    empty = service.classify_instrument(
        {}
    )

    print_result(
        "Empty Holding Identity Safe",
        empty[
            "identity_available"
        ] is False,
    )

    print_result(
        "Empty Holding Classification Safe",
        empty[
            "instrument_classification"
        ] == "UNKNOWN",
    )

    print_result(
        "Empty Holding Structure Safe",
        empty[
            "investment_structure"
        ] == "UNKNOWN",
    )

    print_result(
        "Empty Holding Intelligence Gated",
        empty[
            "instrument_intelligence_available"
        ] is False,
    )

    print_result(
        "Empty Holding Missing Capabilities",
        empty[
            "missing_capabilities"
        ] == [
            "INSTRUMENT_IDENTITY",
            "INSTRUMENT_CLASSIFICATION",
            "INVESTMENT_STRUCTURE",
        ],
    )

    # =====================================================
    # ARCHITECTURE BOUNDARIES
    # =====================================================

    print_result(
        "Imported Portfolio Scope",
        etf[
            "context_scope"
        ] == "IMPORTED_PERSISTED_HOLDINGS",
    )

    print_result(
        "Persisted Metadata Provenance",
        etf[
            "provenance"
        ] == "PERSISTED_HOLDING_METADATA",
    )

    print_result(
        "Underlying Exposure Boundary",
        etf[
            "underlying_exposure_status"
        ] == "NOT_AVAILABLE",
    )

    print_result(
        "Severity Boundary",
        etf[
            "severity_status"
        ] == "NOT_EVALUATED",
    )

    print_result(
        "Health Score Boundary",
        etf[
            "health_score"
        ] == "NOT_AVAILABLE",
    )

    print_result(
        "Target Allocation Boundary",
        etf[
            "target_allocation"
        ] == "NOT_DEFINED",
    )

    print_result(
        "Recommendation Boundary",
        etf[
            "recommendation_status"
        ] == "NOT_PROVIDED",
    )

    # =====================================================
    # PORTFOLIO-LEVEL AGGREGATION
    # =====================================================

    supported_portfolio = (
        service.evaluate_portfolio_instruments(
            [
                {
                    "security_key": "ISIN:INF1",
                    "symbol": "ETF1",
                    "name": "ETF 1",
                    "isin": "INF1",
                    "asset_type": "ETF",
                },
                {
                    "security_key": "ISIN:INE1",
                    "symbol": "EQ1",
                    "name": "Equity 1",
                    "isin": "INE1",
                    "asset_type": "EQUITY",
                },
            ]
        )
    )

    print_result(
        "Portfolio Instrument Count",
        supported_portfolio[
            "instrument_count"
        ] == 2,
    )

    print_result(
        "Portfolio Fully Intelligent Count",
        supported_portfolio[
            "fully_intelligent_instrument_count"
        ] == 2,
    )

    print_result(
        "Portfolio No Incomplete Instruments",
        supported_portfolio[
            "incomplete_instrument_count"
        ] == 0,
    )

    print_result(
        "Portfolio Required Capabilities Available",
        supported_portfolio[
            "available_capabilities"
        ] == [
            "INSTRUMENT_IDENTITY",
            "INSTRUMENT_CLASSIFICATION",
            "INVESTMENT_STRUCTURE",
        ],
    )

    print_result(
        "Portfolio No Missing Capabilities",
        supported_portfolio[
            "missing_capabilities"
        ] == [],
    )

    print_result(
        "Portfolio Instrument Intelligence Available",
        supported_portfolio[
            "portfolio_instrument_intelligence_available"
        ] is True,
    )

    # =====================================================
    # MIXED PORTFOLIO MUST REMAIN GATED
    # =====================================================

    mixed_portfolio = (
        service.evaluate_portfolio_instruments(
            [
                {
                    "security_key": "ISIN:INF1",
                    "symbol": "ETF1",
                    "name": "ETF 1",
                    "isin": "INF1",
                    "asset_type": "ETF",
                },
                {
                    "security_key": "SYMBOL:X",
                    "symbol": "X",
                    "name": "Unknown Instrument",
                    "isin": "",
                    "asset_type": "UNSUPPORTED_TYPE",
                },
            ]
        )
    )

    print_result(
        "Mixed Portfolio Instrument Count",
        mixed_portfolio[
            "instrument_count"
        ] == 2,
    )

    print_result(
        "Mixed Portfolio Fully Intelligent Count",
        mixed_portfolio[
            "fully_intelligent_instrument_count"
        ] == 1,
    )

    print_result(
        "Mixed Portfolio Incomplete Count",
        mixed_portfolio[
            "incomplete_instrument_count"
        ] == 1,
    )

    print_result(
        "Mixed Portfolio Identity Still Available",
        mixed_portfolio[
            "available_capabilities"
        ] == [
            "INSTRUMENT_IDENTITY",
        ],
    )

    print_result(
        "Mixed Portfolio Missing Context Detected",
        mixed_portfolio[
            "missing_capabilities"
        ] == [
            "INSTRUMENT_CLASSIFICATION",
            "INVESTMENT_STRUCTURE",
        ],
    )

    print_result(
        "Mixed Portfolio Intelligence Gated",
        mixed_portfolio[
            "portfolio_instrument_intelligence_available"
        ] is False,
    )

    print_result(
        "Mixed Portfolio Incomplete Instrument Recorded",
        (
            len(
                mixed_portfolio[
                    "incomplete_instruments"
                ]
            ) == 1
            and mixed_portfolio[
                "incomplete_instruments"
            ][0][
                "symbol"
            ] == "X"
        ),
    )

    # =====================================================
    # EMPTY PORTFOLIO SAFETY
    # =====================================================

    empty_portfolio = (
        service.evaluate_portfolio_instruments(
            []
        )
    )

    print_result(
        "Empty Portfolio Instrument Count",
        empty_portfolio[
            "instrument_count"
        ] == 0,
    )

    print_result(
        "Empty Portfolio No Capabilities",
        empty_portfolio[
            "available_capabilities"
        ] == [],
    )

    print_result(
        "Empty Portfolio Required Capabilities Missing",
        empty_portfolio[
            "missing_capabilities"
        ] == [
            "INSTRUMENT_IDENTITY",
            "INSTRUMENT_CLASSIFICATION",
            "INVESTMENT_STRUCTURE",
        ],
    )

    print_result(
        "Empty Portfolio Intelligence Gated",
        empty_portfolio[
            "portfolio_instrument_intelligence_available"
        ] is False,
    )

    # =====================================================
    # AGGREGATION ARCHITECTURE BOUNDARIES
    # =====================================================

    print_result(
        "Portfolio Aggregation Scope",
        supported_portfolio[
            "context_scope"
        ] == "IMPORTED_PERSISTED_HOLDINGS",
    )

    print_result(
        "Portfolio Completeness Still Unconfirmed",
        supported_portfolio[
            "portfolio_completeness"
        ] == "NOT_CONFIRMED",
    )

    print_result(
        "Portfolio Underlying Exposure Boundary",
        supported_portfolio[
            "underlying_exposure_status"
        ] == "NOT_AVAILABLE",
    )

    print_result(
        "Portfolio Severity Boundary",
        supported_portfolio[
            "severity_status"
        ] == "NOT_EVALUATED",
    )

    print_result(
        "Portfolio Health Score Boundary",
        supported_portfolio[
            "health_score"
        ] == "NOT_AVAILABLE",
    )

    print_result(
        "Portfolio Target Allocation Boundary",
        supported_portfolio[
            "target_allocation"
        ] == "NOT_DEFINED",
    )

    print_result(
        "Portfolio Recommendation Boundary",
        supported_portfolio[
            "recommendation_status"
        ] == "NOT_PROVIDED",
    )

    print()
    print("=" * 76)
    print(
        "SPRINT 0.9.7 PORTFOLIO HEALTH "
        "INSTRUMENT INTELLIGENCE TEST: PASS"
    )
    print("=" * 76)


if __name__ == "__main__":
    main()
