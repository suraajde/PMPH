from services.holdings_database import HoldingsDatabase


class PortfolioStatusService:
    """
    Read-only portfolio data and valuation status service.

    This service reports what PMPH can factually determine
    from persisted portfolio records.

    Important:
    updated_at is a database record update timestamp.
    It must not be interpreted as an authoritative
    market-price or NAV observation timestamp.
    """

    def __init__(
        self,
        database_path="data/pmph_portfolio.db",
    ):

        self.database_path = database_path

        self.holdings_database = HoldingsDatabase(
            database_path=database_path,
        )

    def get_portfolio_status(self):
        """
        Return persisted portfolio data-status information.

        Market valuation freshness is intentionally reported
        as not tracked because PMPH does not currently persist
        an authoritative valuation-as-of timestamp.
        """

        holdings = (
            self.holdings_database.list_holdings()
        )

        holding_count = len(
            holdings
        )

        covered_holdings = [
            holding
            for holding in holdings
            if self._has_usable_valuation(
                holding
            )
        ]

        valuation_covered_count = len(
            covered_holdings
        )

        valuation_coverage_percent = (
            (
                valuation_covered_count
                / holding_count
            )
            * 100.0
            if holding_count
            else 0.0
        )

        updated_at_values = [
            holding.updated_at
            for holding in holdings
            if holding.updated_at
            is not None
        ]

        latest_record_update = (
            max(updated_at_values)
            if updated_at_values
            else None
        )

        oldest_record_update = (
            min(updated_at_values)
            if updated_at_values
            else None
        )

        source_files = sorted(
            {
                holding.source_file.strip()
                for holding in holdings
                if holding.source_file
                and holding.source_file.strip()
            }
        )

        return {
            "holding_count": (
                holding_count
            ),
            "valuation_covered_count": (
                valuation_covered_count
            ),
            "valuation_coverage_percent": (
                valuation_coverage_percent
            ),
            "latest_record_update": (
                latest_record_update
            ),
            "oldest_record_update": (
                oldest_record_update
            ),
            "source_file_count": len(
                source_files
            ),
            "source_files": (
                source_files
            ),
            "market_valuation_freshness": (
                "NOT_TRACKED"
            ),
            "market_valuation_as_of": (
                None
            ),
        }

    @staticmethod
    def _has_usable_valuation(
        holding,
    ):
        """
        Determine whether a persisted holding has a
        structurally usable valuation.

        This checks internal numeric consistency only.
        It does not determine market-data freshness.
        """

        quantity = holding.quantity
        current_price = holding.current_price
        current_value = holding.current_value

        if (
            quantity is None
            or current_price is None
            or current_value is None
        ):

            return False

        if quantity < 0:

            return False

        if current_price < 0:

            return False

        if current_value < 0:

            return False

        expected_current_value = (
            quantity
            * current_price
        )

        tolerance = max(
            0.05,
            abs(current_value)
            * 0.0001,
        )

        return (
            abs(
                expected_current_value
                - current_value
            )
            <= tolerance
        )
