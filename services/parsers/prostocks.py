import pandas as pd

from models.portfolio import PortfolioHolding
from services.parsers.common import BaseParser


class ProStocksParser(BaseParser):
    """
    Parser for ProStocks holdings reports.

    Converts the broker-specific Excel format into
    PMPH's universal PortfolioHolding format.
    """

    BROKER_NAME = "ProStocks"

    def parse(self, file_path):
        # -------------------------------------------------
        # Read workbook without assuming a header row
        # -------------------------------------------------
        raw_df = pd.read_excel(
            file_path,
            header=None
        )

        # -------------------------------------------------
        # Locate the real holdings header automatically
        # -------------------------------------------------
        header_row = self._find_header_row(raw_df)

        if header_row is None:
            raise ValueError(
                "Could not locate the ProStocks holdings table."
            )

        # -------------------------------------------------
        # Read the workbook again using detected header
        # -------------------------------------------------
        df = pd.read_excel(
            file_path,
            header=header_row
        )

        # Remove completely empty rows and columns
        df = df.dropna(
            axis=0,
            how="all"
        )

        df = df.dropna(
            axis=1,
            how="all"
        )

        holdings = []

        # -------------------------------------------------
        # Convert broker rows into universal PMPH holdings
        # -------------------------------------------------
        for _, row in df.iterrows():

            scheme_name = self._clean_text(
                row.get("Scheme Name")
            )

            if not scheme_name:
                continue

            quantity = self._to_float(
                row.get("Units")
            )

            invested_value = self._to_float(
                row.get("Invested Value")
            )

            current_value = self._to_float(
                row.get("Current Value")
            )

            profit_loss = self._to_float(
                row.get("Returns")
            )

            average_price = (
                invested_value / quantity
                if quantity != 0
                else 0.0
            )

            current_price = (
                current_value / quantity
                if quantity != 0
                else 0.0
            )

            profit_loss_percent = (
                (profit_loss / invested_value) * 100
                if invested_value != 0
                else 0.0
            )

            holding = PortfolioHolding(
                broker=self.BROKER_NAME,

                asset_type=self._detect_asset_type(
                    row
                ),

                symbol=scheme_name,
                name=scheme_name,

                isin="",

                quantity=quantity,

                average_price=average_price,
                current_price=current_price,

                invested_value=invested_value,
                current_value=current_value,

                profit_loss=profit_loss,

                profit_loss_percent=profit_loss_percent
            )

            holdings.append(holding)

        return holdings

    # =====================================================
    # Header Detection
    # =====================================================

    def _find_header_row(self, dataframe):
        """
        Find the row containing the actual holdings headers.

        This avoids relying on a fixed Excel row number.
        """

        for index, row in dataframe.iterrows():

            values = [
                str(value).strip().lower()
                for value in row.tolist()
                if pd.notna(value)
            ]

            if (
                "scheme name" in values
                and "units" in values
                and "invested value" in values
            ):
                return index

        return None

    # =====================================================
    # Asset Classification
    # =====================================================

    def _detect_asset_type(self, row):

        category = self._clean_text(
            row.get("Category")
        ).upper()

        amc = self._clean_text(
            row.get("AMC")
        ).upper()

        if category == "ETF" or amc == "ETF":
            return "ETF"

        if "MUTUAL" in category:
            return "Mutual Fund"

        return category if category else "Unknown"

    # =====================================================
    # Utility Methods
    # =====================================================

    @staticmethod
    def _clean_text(value):

        if pd.isna(value):
            return ""

        return str(value).strip()

    @staticmethod
    def _to_float(value):

        if pd.isna(value):
            return 0.0

        try:
            return float(value)

        except (TypeError, ValueError):
            return 0.0