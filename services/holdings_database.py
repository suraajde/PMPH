import sqlite3
from datetime import datetime

from models.stored_holding import StoredHolding


class HoldingsDatabase:
    """
    Persistent current-holdings storage for PMPH.

    Security matching:
    1. Prefer ISIN.
    2. Fall back to normalized symbol.

    Re-importing the same security for the same account
    updates the existing holding instead of duplicating it.
    """

    def __init__(
        self,
        database_path="data/pmph_portfolio.db",
    ):

        self.database_path = (
            database_path
        )

        self.initialize_database()

    def _connect(self):

        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = (
            sqlite3.Row
        )

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def initialize_database(self):

        with self._connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS holdings
                (
                    holding_id TEXT PRIMARY KEY,

                    account_id TEXT NOT NULL,

                    security_key TEXT NOT NULL,

                    symbol TEXT,

                    name TEXT,

                    isin TEXT,

                    asset_type TEXT,

                    quantity REAL NOT NULL,

                    average_price REAL NOT NULL,

                    current_price REAL NOT NULL,

                    invested_value REAL NOT NULL,

                    current_value REAL NOT NULL,

                    profit_loss REAL NOT NULL,

                    profit_loss_percent REAL NOT NULL,

                    source_file TEXT,

                    imported_at TEXT NOT NULL,

                    updated_at TEXT NOT NULL,

                    UNIQUE
                    (
                        account_id,
                        security_key
                    ),

                    FOREIGN KEY
                    (
                        account_id
                    )
                    REFERENCES accounts
                    (
                        account_id
                    )
                    ON DELETE CASCADE
                )
                """
            )

            connection.commit()

    # =====================================================
    # SAVE / UPDATE HOLDING
    # =====================================================

    def save_holding(
        self,
        holding: StoredHolding,
    ):

        errors = holding.validate()

        if errors:

            raise ValueError(
                "Invalid holding: "
                + "; ".join(
                    errors
                )
            )

        security_key = (
            holding.security_key()
        )

        existing = (
            self.find_holding(
                account_id=holding.account_id,
                security_key=security_key,
            )
        )

        now = datetime.now()

        if existing:

            holding.holding_id = (
                existing.holding_id
            )

            holding.imported_at = (
                existing.imported_at
            )

            holding.updated_at = now

            with self._connect() as connection:

                connection.execute(
                    """
                    UPDATE holdings

                    SET
                        symbol = ?,
                        name = ?,
                        isin = ?,
                        asset_type = ?,
                        quantity = ?,
                        average_price = ?,
                        current_price = ?,
                        invested_value = ?,
                        current_value = ?,
                        profit_loss = ?,
                        profit_loss_percent = ?,
                        source_file = ?,
                        updated_at = ?

                    WHERE
                        account_id = ?
                        AND security_key = ?
                    """,
                    (
                        holding.symbol,
                        holding.name,
                        holding.isin,
                        holding.asset_type,
                        holding.quantity,
                        holding.average_price,
                        holding.current_price,
                        holding.invested_value,
                        holding.current_value,
                        holding.profit_loss,
                        holding.profit_loss_percent,
                        holding.source_file,
                        holding.updated_at.isoformat(),
                        holding.account_id,
                        security_key,
                    ),
                )

                connection.commit()

            return holding

        holding.imported_at = now
        holding.updated_at = now

        with self._connect() as connection:

            connection.execute(
                """
                INSERT INTO holdings
                (
                    holding_id,
                    account_id,
                    security_key,
                    symbol,
                    name,
                    isin,
                    asset_type,
                    quantity,
                    average_price,
                    current_price,
                    invested_value,
                    current_value,
                    profit_loss,
                    profit_loss_percent,
                    source_file,
                    imported_at,
                    updated_at
                )

                VALUES
                (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    holding.holding_id,
                    holding.account_id,
                    security_key,
                    holding.symbol,
                    holding.name,
                    holding.isin,
                    holding.asset_type,
                    holding.quantity,
                    holding.average_price,
                    holding.current_price,
                    holding.invested_value,
                    holding.current_value,
                    holding.profit_loss,
                    holding.profit_loss_percent,
                    holding.source_file,
                    holding.imported_at.isoformat(),
                    holding.updated_at.isoformat(),
                ),
            )

            connection.commit()

        return holding

    # =====================================================
    # DELETE ONE HOLDING
    # =====================================================

    def delete_holding(
        self,
        holding_id,
    ):

        with self._connect() as connection:

            cursor = connection.execute(
                """
                DELETE FROM holdings
                WHERE holding_id = ?
                """,
                (
                    holding_id,
                ),
            )

            connection.commit()

        return (
            cursor.rowcount > 0
        )

    # =====================================================
    # FIND HOLDING
    # =====================================================

    def find_holding(
        self,
        account_id,
        security_key,
    ):

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT *
                FROM holdings

                WHERE
                    account_id = ?
                    AND security_key = ?

                LIMIT 1
                """,
                (
                    account_id,
                    security_key,
                ),
            ).fetchone()

        if row is None:

            return None

        return self._row_to_holding(
            row
        )

    # =====================================================
    # LIST HOLDINGS
    # =====================================================

    def list_holdings(
        self,
        account_id=None,
    ):

        if account_id:

            query = """
                SELECT *
                FROM holdings
                WHERE account_id = ?
                ORDER BY symbol
            """

            parameters = (
                account_id,
            )

        else:

            query = """
                SELECT *
                FROM holdings
                ORDER BY account_id, symbol
            """

            parameters = ()

        with self._connect() as connection:

            rows = connection.execute(
                query,
                parameters,
            ).fetchall()

        return [
            self._row_to_holding(
                row
            )
            for row in rows
        ]

    # =====================================================
    # COUNT HOLDINGS
    # =====================================================

    def count_holdings(
        self,
        account_id=None,
    ):

        if account_id:

            query = """
                SELECT COUNT(*) AS total
                FROM holdings
                WHERE account_id = ?
            """

            parameters = (
                account_id,
            )

        else:

            query = """
                SELECT COUNT(*) AS total
                FROM holdings
            """

            parameters = ()

        with self._connect() as connection:

            row = connection.execute(
                query,
                parameters,
            ).fetchone()

        return int(
            row[
                "total"
            ]
        )

    # =====================================================
    # ROW CONVERSION
    # =====================================================

    @staticmethod
    def _row_to_holding(
        row,
    ):

        return StoredHolding(
            holding_id=row[
                "holding_id"
            ],

            account_id=row[
                "account_id"
            ],

            symbol=row[
                "symbol"
            ]
            or "",

            name=row[
                "name"
            ]
            or "",

            isin=row[
                "isin"
            ]
            or "",

            asset_type=row[
                "asset_type"
            ]
            or "",

            quantity=float(
                row[
                    "quantity"
                ]
            ),

            average_price=float(
                row[
                    "average_price"
                ]
            ),

            current_price=float(
                row[
                    "current_price"
                ]
            ),

            invested_value=float(
                row[
                    "invested_value"
                ]
            ),

            current_value=float(
                row[
                    "current_value"
                ]
            ),

            profit_loss=float(
                row[
                    "profit_loss"
                ]
            ),

            profit_loss_percent=float(
                row[
                    "profit_loss_percent"
                ]
            ),

            source_file=row[
                "source_file"
            ],

            imported_at=datetime.fromisoformat(
                row[
                    "imported_at"
                ]
            ),

            updated_at=datetime.fromisoformat(
                row[
                    "updated_at"
                ]
            ),
        )