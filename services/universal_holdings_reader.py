import os

import pandas as pd

from models.portfolio import PortfolioHolding


class UniversalHoldingsReader:
    """
    Content-driven universal holdings reader.

    This reader does not require a broker-specific format.

    It attempts to:
    1. Find the holdings sheet automatically.
    2. Find the holdings-table header automatically.
    3. Understand equivalent financial column names.
    4. Map them into PMPH's universal format.
    5. Derive missing financial values where safely possible.
    """

    # =====================================================
    # UNIVERSAL COLUMN VOCABULARY
    # =====================================================

    COLUMN_ALIASES = {

        "symbol": {
            "symbol",
            "ticker",
            "trading symbol",
            "security symbol",
            "scrip code",
            "scheme code",
        },

        "name": {
            "name",
            "security",
            "security name",
            "stock name",
            "company",
            "company name",
            "scheme",
            "scheme name",
            "instrument",
            "instrument name",
            "description",
        },

        "isin": {
            "isin",
            "isin code",
            "security isin",
        },

        "quantity": {
            "quantity",
            "qty",
            "units",
            "unit",
            "balance units",
            "available qty",
            "available quantity",
            "quantity available",
            "net qty",
            "net quantity",
            "holding quantity",
            "total qty",
            "total quantity",
        },

        "average_price": {
            "average price",
            "avg price",
            "avg. price",
            "average buy price",
            "avg buy price",
            "average cost",
            "avg cost",
            "avg. cost",
            "purchase price",
            "purchase nav",
            "average nav",
            "avg nav",
        },

        "current_price": {
            "current price",
            "market price",
            "closing price",
            "close price",
            "previous closing price",
            "ltp",
            "last traded price",
            "cmp",
            "current nav",
            "nav",
        },

        "invested_value": {
            "invested value",
            "investment value",
            "invested amount",
            "investment amount",
            "cost value",
            "cost amount",
            "total cost",
            "buy value",
            "purchase value",
        },

        "current_value": {
            "current value",
            "market value",
            "present value",
            "portfolio value",
            "closing value",
            "valuation",
            "market amount",
        },

        "profit_loss": {
            "profit/loss",
            "profit / loss",
            "profit loss",
            "p/l",
            "p&l",
            "unrealised p&l",
            "unrealized p&l",
            "unrealised profit/loss",
            "unrealized profit/loss",
            "returns",
            "gain/loss",
        },

        "profit_loss_percent": {
            "profit/loss %",
            "profit / loss %",
            "profit loss %",
            "p/l %",
            "p&l %",
            "unrealised p&l %",
            "unrealized p&l %",
            "unrealized p&l pct.",
            "unrealised p&l pct.",
            "unrealized p&l pct",
            "unrealised p&l pct",
            "return %",
            "returns %",
            "gain/loss %",
        },

        "asset_type": {
            "asset type",
            "instrument type",
            "security type",
            "category",
            "product type",
            "sector",
        },
    }

    # =====================================================
    # PUBLIC METHODS
    # =====================================================

    def inspect(self, file_path):
        """
        Inspect the file and locate the most likely holdings table.
        """

        extension = os.path.splitext(
            file_path
        )[1].lower()

        if extension in {
            ".xlsx",
            ".xls",
        }:

            return self._inspect_excel(
                file_path
            )

        if extension == ".csv":

            return self._inspect_csv(
                file_path
            )

        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    def read(self, file_path):
        """
        Detect and extract holdings into PMPH's universal format.

        Returns:
            detection_result, holdings
        """

        detection = self.inspect(
            file_path
        )

        if not detection["detected"]:

            raise ValueError(
                "A reliable holdings table could not be detected."
            )

        dataframe = self._load_detected_table(
            file_path,
            detection
        )

        holdings = self._extract_holdings(
            dataframe,
            detection["mapping"]
        )

        return (
            detection,
            holdings,
        )

    # =====================================================
    # EXCEL INSPECTION
    # =====================================================

    def _inspect_excel(
        self,
        file_path
    ):

        workbook = pd.ExcelFile(
            file_path
        )

        candidates = []

        for sheet_name in workbook.sheet_names:

            raw_df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                header=None
            )

            candidate = self._find_best_header(
                raw_df
            )

            if candidate is not None:

                candidate[
                    "sheet_name"
                ] = sheet_name

                candidates.append(
                    candidate
                )

        return self._build_result(
            candidates
        )

    # =====================================================
    # CSV INSPECTION
    # =====================================================

    def _inspect_csv(
        self,
        file_path
    ):

        raw_df = pd.read_csv(
            file_path,
            header=None
        )

        candidate = self._find_best_header(
            raw_df
        )

        candidates = []

        if candidate is not None:

            candidate[
                "sheet_name"
            ] = "CSV"

            candidates.append(
                candidate
            )

        return self._build_result(
            candidates
        )

    # =====================================================
    # LOAD DETECTED HOLDINGS TABLE
    # =====================================================

    def _load_detected_table(
        self,
        file_path,
        detection
    ):

        extension = os.path.splitext(
            file_path
        )[1].lower()

        if extension in {
            ".xlsx",
            ".xls",
        }:

            dataframe = pd.read_excel(
                file_path,
                sheet_name=detection[
                    "sheet_name"
                ],
                header=detection[
                    "header_row"
                ]
            )

        elif extension == ".csv":

            dataframe = pd.read_csv(
                file_path,
                header=detection[
                    "header_row"
                ]
            )

        else:

            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        dataframe = dataframe.dropna(
            axis=0,
            how="all"
        )

        dataframe = dataframe.dropna(
            axis=1,
            how="all"
        )

        return dataframe

    # =====================================================
    # HEADER DISCOVERY
    # =====================================================

    def _find_best_header(
        self,
        dataframe
    ):

        best_candidate = None

        rows_to_scan = min(
            len(dataframe),
            100
        )

        for row_index in range(
            rows_to_scan
        ):

            row = dataframe.iloc[
                row_index
            ]

            mapping = self._map_columns(
                row.tolist()
            )

            score = self._score_mapping(
                mapping
            )

            if score <= 0:
                continue

            candidate = {

                "header_row":
                    row_index,

                "mapping":
                    mapping,

                "score":
                    score,

                "matched_fields":
                    list(
                        mapping.keys()
                    ),
            }

            if (
                best_candidate is None
                or score
                > best_candidate[
                    "score"
                ]
            ):

                best_candidate = (
                    candidate
                )

        return best_candidate

    # =====================================================
    # UNIVERSAL COLUMN MAPPING
    # =====================================================

    def _map_columns(
        self,
        row_values
    ):

        mapping = {}

        for (
            column_index,
            value
        ) in enumerate(
            row_values
        ):

            normalized = (
                self._normalize_text(
                    value
                )
            )

            if not normalized:
                continue

            detected_field = (
                self._detect_field(
                    normalized
                )
            )

            if (
                detected_field
                and detected_field
                not in mapping
            ):

                mapping[
                    detected_field
                ] = {

                    "column_index":
                        column_index,

                    "original_name":
                        str(
                            value
                        ).strip(),
                }

        return mapping

    def _detect_field(
        self,
        normalized_name
    ):

        for (
            standard_field,
            aliases
        ) in self.COLUMN_ALIASES.items():

            for alias in aliases:

                if (
                    normalized_name
                    == self._normalize_text(
                        alias
                    )
                ):

                    return standard_field

        return None

    # =====================================================
    # DETECTION SCORING
    # =====================================================

    def _score_mapping(
        self,
        mapping
    ):

        score = 0

        identity_fields = {
            "symbol",
            "name",
            "isin",
        }

        if (
            identity_fields
            & mapping.keys()
        ):

            score += 3

        if (
            "quantity"
            in mapping
        ):

            score += 3

        valuation_fields = {
            "average_price",
            "current_price",
            "invested_value",
            "current_value",
        }

        score += (
            len(
                valuation_fields
                & mapping.keys()
            )
            * 2
        )

        if (
            "profit_loss"
            in mapping
        ):

            score += 1

        if (
            "profit_loss_percent"
            in mapping
        ):

            score += 1

        return score

    # =====================================================
    # DETECTION RESULT
    # =====================================================

    def _build_result(
        self,
        candidates
    ):

        if not candidates:

            return {

                "detected":
                    False,

                "confidence":
                    "LOW",

                "message":
                    (
                        "No reliable holdings "
                        "table was detected."
                    ),

                "sheet_name":
                    None,

                "header_row":
                    None,

                "mapping":
                    {},

                "matched_fields":
                    [],

                "score":
                    0,
            }

        best = max(
            candidates,
            key=lambda item:
                item["score"]
        )

        confidence = (
            self._confidence_level(
                best
            )
        )

        return {

            "detected":
                confidence
                != "LOW",

            "confidence":
                confidence,

            "message":
                (
                    "Potential holdings table "
                    "detected by content."
                ),

            "sheet_name":
                best[
                    "sheet_name"
                ],

            "header_row":
                best[
                    "header_row"
                ],

            "mapping":
                best[
                    "mapping"
                ],

            "matched_fields":
                best[
                    "matched_fields"
                ],

            "score":
                best[
                    "score"
                ],
        }

    def _confidence_level(
        self,
        candidate
    ):

        mapping = candidate[
            "mapping"
        ]

        has_identity = bool(
            {
                "symbol",
                "name",
                "isin",
            }
            & mapping.keys()
        )

        has_quantity = (
            "quantity"
            in mapping
        )

        has_valuation = bool(
            {
                "average_price",
                "current_price",
                "invested_value",
                "current_value",
            }
            & mapping.keys()
        )

        if (
            has_identity
            and has_quantity
            and has_valuation
            and candidate[
                "score"
            ] >= 10
        ):

            return "HIGH"

        if (
            has_identity
            and has_quantity
        ):

            return "MEDIUM"

        return "LOW"

    # =====================================================
    # UNIVERSAL HOLDINGS EXTRACTION
    # =====================================================

    def _extract_holdings(
        self,
        dataframe,
        mapping
    ):

        holdings = []

        for _, row in dataframe.iterrows():

            name = self._get_text_value(
                row,
                mapping,
                "name"
            )

            symbol = self._get_text_value(
                row,
                mapping,
                "symbol"
            )

            isin = self._get_text_value(
                row,
                mapping,
                "isin"
            )

            # ---------------------------------------------
            # A holding must have some identity
            # ---------------------------------------------

            if not any(
                [
                    name,
                    symbol,
                    isin,
                ]
            ):

                continue

            quantity = (
                self._get_number_value(
                    row,
                    mapping,
                    "quantity"
                )
            )

            average_price = (
                self._get_number_value(
                    row,
                    mapping,
                    "average_price"
                )
            )

            current_price = (
                self._get_number_value(
                    row,
                    mapping,
                    "current_price"
                )
            )

            invested_value = (
                self._get_number_value(
                    row,
                    mapping,
                    "invested_value"
                )
            )

            current_value = (
                self._get_number_value(
                    row,
                    mapping,
                    "current_value"
                )
            )

            profit_loss = (
                self._get_number_value(
                    row,
                    mapping,
                    "profit_loss"
                )
            )

            profit_loss_percent = (
                self._get_number_value(
                    row,
                    mapping,
                    "profit_loss_percent"
                )
            )

            asset_type = (
                self._get_text_value(
                    row,
                    mapping,
                    "asset_type"
                )
            )

            # ---------------------------------------------
            # DERIVE MISSING FINANCIAL VALUES
            # ---------------------------------------------

            if (
                average_price == 0
                and invested_value != 0
                and quantity != 0
            ):

                average_price = (
                    invested_value
                    / quantity
                )

            if (
                current_price == 0
                and current_value != 0
                and quantity != 0
            ):

                current_price = (
                    current_value
                    / quantity
                )

            if (
                invested_value == 0
                and average_price != 0
                and quantity != 0
            ):

                invested_value = (
                    average_price
                    * quantity
                )

            if (
                current_value == 0
                and current_price != 0
                and quantity != 0
            ):

                current_value = (
                    current_price
                    * quantity
                )

            if (
                profit_loss == 0
                and (
                    current_value != 0
                    or invested_value != 0
                )
            ):

                profit_loss = (
                    current_value
                    - invested_value
                )

            if (
                profit_loss_percent == 0
                and invested_value != 0
            ):

                profit_loss_percent = (
                    profit_loss
                    / invested_value
                    * 100
                )

            # ---------------------------------------------
            # SKIP OBVIOUS NON-HOLDING ROWS
            # ---------------------------------------------

            if (
                quantity == 0
                and invested_value == 0
                and current_value == 0
            ):

                continue

            display_name = (
                name
                or symbol
                or isin
            )

            display_symbol = (
                symbol
                or name
                or isin
            )

            holding = PortfolioHolding(

                broker="Auto-Detected",

                asset_type=(
                    asset_type
                    or "Unknown"
                ),

                symbol=display_symbol,

                name=display_name,

                isin=isin,

                quantity=quantity,

                average_price=average_price,

                current_price=current_price,

                invested_value=invested_value,

                current_value=current_value,

                profit_loss=profit_loss,

                profit_loss_percent=(
                    profit_loss_percent
                ),
            )

            holdings.append(
                holding
            )

        return holdings

    # =====================================================
    # DYNAMIC ROW ACCESS
    # =====================================================

    def _get_raw_value(
        self,
        row,
        mapping,
        field_name
    ):

        field = mapping.get(
            field_name
        )

        if field is None:
            return None

        original_name = field[
            "original_name"
        ]

        if (
            original_name
            not in row.index
        ):

            return None

        return row[
            original_name
        ]

    def _get_text_value(
        self,
        row,
        mapping,
        field_name
    ):

        value = self._get_raw_value(
            row,
            mapping,
            field_name
        )

        if value is None:
            return ""

        if pd.isna(value):
            return ""

        return str(
            value
        ).strip()

    def _get_number_value(
        self,
        row,
        mapping,
        field_name
    ):

        value = self._get_raw_value(
            row,
            mapping,
            field_name
        )

        return self._to_float(
            value
        )

    # =====================================================
    # UTILITIES
    # =====================================================

    @staticmethod
    def _normalize_text(
        value
    ):

        if pd.isna(value):
            return ""

        text = str(
            value
        ).strip().lower()

        text = " ".join(
            text.split()
        )

        return text

    @staticmethod
    def _to_float(
        value
    ):

        if value is None:
            return 0.0

        if pd.isna(value):
            return 0.0

        if isinstance(
            value,
            str
        ):

            cleaned = (
                value
                .replace(",", "")
                .replace("₹", "")
                .replace("%", "")
                .strip()
            )

            if not cleaned:
                return 0.0

            try:

                return float(
                    cleaned
                )

            except ValueError:

                return 0.0

        try:

            return float(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            return 0.0