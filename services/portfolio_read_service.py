from services.portfolio_database import PortfolioDatabase
from services.holdings_database import HoldingsDatabase


class PortfolioReadService:
    """
    Read-only portfolio query service for PMPH.

    Responsibilities:
    - Read persisted portfolio accounts.
    - Read holdings account-wise.
    - Provide consolidated portfolio views.
    - Calculate portfolio-level summaries.

    This service must not modify portfolio data.
    """

    def __init__(
        self,
        database_path="data/pmph_portfolio.db",
    ):

        self.database_path = database_path

        self.portfolio_database = PortfolioDatabase(
            database_path=database_path,
        )

        self.holdings_database = HoldingsDatabase(
            database_path=database_path,
        )

    # =====================================================
    # GET ACCOUNT PORTFOLIO
    # =====================================================

    def get_account_portfolio(
        self,
        account_id,
    ):
        """
        Return one persisted account together with
        all holdings belonging to that account.

        Returns None if the account does not exist.
        """

        account = (
            self.portfolio_database.get_account(
                account_id
            )
        )

        if account is None:

            return None

        holdings = (
            self.holdings_database.list_holdings(
                account_id=account_id
            )
        )

        return {
            "account": account,
            "holdings": holdings,
            "holding_count": len(
                holdings
            ),
        }

    # =====================================================
    # GET ALL ACCOUNT PORTFOLIOS
    # =====================================================

    def get_all_account_portfolios(
        self,
        active_only=False,
    ):
        """
        Return all persisted portfolio accounts together
        with their account-wise holdings.
        """

        accounts = (
            self.portfolio_database.list_accounts(
                active_only=active_only
            )
        )

        portfolios = []

        for account in accounts:

            holdings = (
                self.holdings_database.list_holdings(
                    account_id=account.account_id
                )
            )

            portfolios.append(
                {
                    "account": account,
                    "holdings": holdings,
                    "holding_count": len(
                        holdings
                    ),
                }
            )

        return portfolios

    # =====================================================
    # GET CONSOLIDATED HOLDINGS
    # =====================================================

    def get_consolidated_holdings(self):
        """
        Consolidate the same security across all accounts.

        Security matching follows StoredHolding.security_key():
        ISIN is preferred, with normalized symbol as fallback.

        Account-wise persisted holdings are not modified.
        """

        holdings = (
            self.holdings_database.list_holdings()
        )

        consolidated = {}

        for holding in holdings:

            security_key = (
                holding.security_key()
            )

            if security_key not in consolidated:

                consolidated[
                    security_key
                ] = {
                    "security_key": security_key,
                    "symbol": holding.symbol,
                    "name": holding.name,
                    "isin": holding.isin,
                    "asset_type": holding.asset_type,
                    "quantity": 0.0,
                    "invested_value": 0.0,
                    "current_value": 0.0,
                    "profit_loss": 0.0,
                    "account_ids": set(),
                }

            item = consolidated[
                security_key
            ]

            item["quantity"] += (
                holding.quantity
            )

            item["invested_value"] += (
                holding.invested_value
            )

            item["current_value"] += (
                holding.current_value
            )

            item["profit_loss"] += (
                holding.profit_loss
            )

            item["account_ids"].add(
                holding.account_id
            )

        results = []

        for item in consolidated.values():

            quantity = item[
                "quantity"
            ]

            invested_value = item[
                "invested_value"
            ]

            current_value = item[
                "current_value"
            ]

            item["average_price"] = (
                invested_value / quantity
                if quantity
                else 0.0
            )

            item["current_price"] = (
                current_value / quantity
                if quantity
                else 0.0
            )

            item["profit_loss_percent"] = (
                (
                    item["profit_loss"]
                    / invested_value
                )
                * 100.0
                if invested_value
                else 0.0
            )

            item["account_ids"] = sorted(
                item["account_ids"]
            )

            item["account_count"] = len(
                item["account_ids"]
            )

            results.append(
                item
            )

        return sorted(
            results,
            key=lambda item: (
                item["symbol"] or ""
            ).upper(),
        )

    # =====================================================
    # GET PORTFOLIO SUMMARY
    # =====================================================

    def get_portfolio_summary(self):
        """
        Return consolidated portfolio-level totals.
        """

        holdings = (
            self.holdings_database.list_holdings()
        )

        accounts = (
            self.portfolio_database.list_accounts()
        )

        invested_value = sum(
            holding.invested_value
            for holding in holdings
        )

        current_value = sum(
            holding.current_value
            for holding in holdings
        )

        profit_loss = (
            current_value
            - invested_value
        )

        profit_loss_percent = (
            (
                profit_loss
                / invested_value
            )
            * 100.0
            if invested_value
            else 0.0
        )

        consolidated_holdings = (
            self.get_consolidated_holdings()
        )

        return {
            "account_count": len(
                accounts
            ),
            "holding_count": len(
                holdings
            ),
            "consolidated_holding_count": len(
                consolidated_holdings
            ),
            "invested_value": invested_value,
            "current_value": current_value,
            "profit_loss": profit_loss,
            "profit_loss_percent": (
                profit_loss_percent
            ),
        }
