from services.portfolio_read_service import PortfolioReadService


class PortfolioAnalyticsService:
    """
    Read-only portfolio analytics service for PMPH.

    Responsibilities:
    - Calculate observable portfolio concentration.
    - Calculate persisted security-position allocation.
    - Calculate account concentration.
    - Calculate asset-type concentration.

    Important boundary:
    These analytics describe persisted portfolio positions only.

    They do not inspect ETF/fund constituents and therefore must not
    be interpreted as underlying security diversification or overlap
    analysis.
    """

    def __init__(
        self,
        database_path="data/pmph_portfolio.db",
    ):

        self.database_path = database_path

        self.read_service = PortfolioReadService(
            database_path=database_path,
        )

    # =====================================================
    # SECURITY CONCENTRATION
    # =====================================================

    def get_security_concentration(self):

        holdings = (
            self.read_service
            .get_consolidated_holdings()
        )

        total_current_value = sum(
            holding["current_value"]
            for holding in holdings
        )

        rows = []

        for holding in holdings:

            current_value = float(
                holding["current_value"]
            )

            weight = (
                current_value
                / total_current_value
                if total_current_value
                else 0.0
            )

            rows.append(
                {
                    "security_key": holding[
                        "security_key"
                    ],
                    "symbol": holding[
                        "symbol"
                    ],
                    "asset_type": holding[
                        "asset_type"
                    ],
                    "current_value": (
                        current_value
                    ),
                    "weight": weight,
                    "weight_percent": (
                        weight * 100.0
                    ),
                }
            )

        rows.sort(
            key=lambda row: row["weight"],
            reverse=True,
        )

        for index, row in enumerate(
            rows,
            start=1,
        ):

            row["rank"] = index

        largest_weight = (
            rows[0]["weight"]
            if rows
            else 0.0
        )

        top_3_weight = sum(
            row["weight"]
            for row in rows[:3]
        )

        hhi = sum(
            row["weight"] ** 2
            for row in rows
        )

        effective_positions = (
            1.0 / hhi
            if hhi
            else 0.0
        )

        return {
            "security_count": len(rows),
            "total_current_value": (
                total_current_value
            ),
            "largest_position_weight": (
                largest_weight
            ),
            "largest_position_percent": (
                largest_weight * 100.0
            ),
            "top_3_weight": top_3_weight,
            "top_3_percent": (
                top_3_weight * 100.0
            ),
            "hhi": hhi,
            "effective_security_positions": (
                effective_positions
            ),
            "positions": rows,
            "scope": (
                "PERSISTED_SECURITY_POSITIONS"
            ),
        }

    # =====================================================
    # ACCOUNT CONCENTRATION
    # =====================================================

    def get_account_concentration(self):

        portfolios = (
            self.read_service
            .get_all_account_portfolios()
        )

        rows = []

        for portfolio in portfolios:

            account = portfolio["account"]

            current_value = sum(
                holding.current_value
                for holding in portfolio[
                    "holdings"
                ]
            )

            rows.append(
                {
                    "account_id": (
                        account.account_id
                    ),
                    "owner_name": (
                        account.owner_name
                    ),
                    "platform_name": (
                        account.platform_name
                    ),
                    "account_name": (
                        account.account_name
                    ),
                    "current_value": float(
                        current_value
                    ),
                }
            )

        total_current_value = sum(
            row["current_value"]
            for row in rows
        )

        for row in rows:

            weight = (
                row["current_value"]
                / total_current_value
                if total_current_value
                else 0.0
            )

            row["weight"] = weight
            row["weight_percent"] = (
                weight * 100.0
            )

        rows.sort(
            key=lambda row: row["weight"],
            reverse=True,
        )

        largest_weight = (
            rows[0]["weight"]
            if rows
            else 0.0
        )

        hhi = sum(
            row["weight"] ** 2
            for row in rows
        )

        return {
            "account_count": len(rows),
            "total_current_value": (
                total_current_value
            ),
            "largest_account_weight": (
                largest_weight
            ),
            "largest_account_percent": (
                largest_weight * 100.0
            ),
            "hhi": hhi,
            "accounts": rows,
        }

    # =====================================================
    # ASSET TYPE CONCENTRATION
    # =====================================================

    def get_asset_type_concentration(self):

        holdings = (
            self.read_service
            .get_consolidated_holdings()
        )

        totals = {}

        for holding in holdings:

            asset_type = (
                holding["asset_type"]
                or "Unknown"
            )

            totals[asset_type] = (
                totals.get(
                    asset_type,
                    0.0,
                )
                + float(
                    holding["current_value"]
                )
            )

        total_current_value = sum(
            totals.values()
        )

        rows = []

        for asset_type, current_value in (
            totals.items()
        ):

            weight = (
                current_value
                / total_current_value
                if total_current_value
                else 0.0
            )

            rows.append(
                {
                    "asset_type": asset_type,
                    "current_value": (
                        current_value
                    ),
                    "weight": weight,
                    "weight_percent": (
                        weight * 100.0
                    ),
                }
            )

        rows.sort(
            key=lambda row: row["weight"],
            reverse=True,
        )

        hhi = sum(
            row["weight"] ** 2
            for row in rows
        )

        return {
            "asset_type_count": len(rows),
            "total_current_value": (
                total_current_value
            ),
            "hhi": hhi,
            "asset_types": rows,
            "scope": (
                "PERSISTED_ASSET_TYPE_METADATA"
            ),
        }

    # =====================================================
    # CONCENTRATION SUMMARY
    # =====================================================

    def get_concentration_summary(self):

        security = (
            self.get_security_concentration()
        )

        account = (
            self.get_account_concentration()
        )

        asset_type = (
            self.get_asset_type_concentration()
        )

        return {
            "security_count": security[
                "security_count"
            ],
            "largest_position_percent": (
                security[
                    "largest_position_percent"
                ]
            ),
            "top_3_percent": security[
                "top_3_percent"
            ],
            "security_hhi": security[
                "hhi"
            ],
            "effective_security_positions": (
                security[
                    "effective_security_positions"
                ]
            ),
            "account_count": account[
                "account_count"
            ],
            "largest_account_percent": (
                account[
                    "largest_account_percent"
                ]
            ),
            "account_hhi": account[
                "hhi"
            ],
            "asset_type_count": asset_type[
                "asset_type_count"
            ],
            "asset_type_hhi": asset_type[
                "hhi"
            ],
            "underlying_diversification": (
                "NOT_AVAILABLE"
            ),
            "fund_etf_overlap": (
                "NOT_AVAILABLE"
            ),
        }
