import os
import sqlite3
from datetime import datetime

from models.account import PortfolioAccount


class PortfolioDatabase:
    """
    Persistent SQLite storage foundation for PMPH.

    Responsibilities:
    - Create and maintain the PMPH database.
    - Store portfolio owners/accounts.
    - Prevent duplicate account records.
    - Provide account lookup for future holdings imports.

    Holdings persistence will be added after the account
    database layer has been independently tested.
    """

    def __init__(
        self,
        database_path="data/pmph_portfolio.db",
    ):

        self.database_path = database_path

        database_directory = os.path.dirname(
            self.database_path
        )

        if database_directory:

            os.makedirs(
                database_directory,
                exist_ok=True,
            )

        self.initialize_database()

    # =====================================================
    # CONNECTION
    # =====================================================

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
    # DATABASE INITIALIZATION
    # =====================================================

    def initialize_database(self):

        with self._connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS accounts
                (
                    account_id TEXT PRIMARY KEY,

                    owner_name TEXT NOT NULL,

                    platform_name TEXT NOT NULL,

                    account_name TEXT NOT NULL,

                    external_account_reference TEXT,

                    is_active INTEGER NOT NULL DEFAULT 1,

                    created_at TEXT NOT NULL,

                    updated_at TEXT NOT NULL,

                    UNIQUE
                    (
                        owner_name,
                        platform_name,
                        account_name
                    )
                )
                """
            )

            connection.commit()

    # =====================================================
    # SAVE ACCOUNT
    # =====================================================

    def save_account(
        self,
        account: PortfolioAccount,
    ):

        errors = account.validate()

        if errors:

            raise ValueError(
                "Invalid portfolio account: "
                + "; ".join(
                    errors
                )
            )

        existing = (
            self.find_account(
                owner_name=account.owner_name,
                platform_name=account.platform_name,
                account_name=account.account_name,
            )
        )

        if existing:

            return existing

        now = datetime.now()

        account.created_at = now
        account.updated_at = now

        with self._connect() as connection:

            connection.execute(
                """
                INSERT INTO accounts
                (
                    account_id,
                    owner_name,
                    platform_name,
                    account_name,
                    external_account_reference,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES
                (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
                """,
                (
                    account.account_id,
                    account.owner_name.strip(),
                    account.platform_name.strip(),
                    account.account_name.strip(),
                    account.external_account_reference,
                    1 if account.is_active else 0,
                    account.created_at.isoformat(),
                    account.updated_at.isoformat(),
                ),
            )

            connection.commit()

        return account

    # =====================================================
    # FIND ACCOUNT
    # =====================================================

    def find_account(
        self,
        owner_name,
        platform_name,
        account_name,
    ):

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT *
                FROM accounts
                WHERE
                    LOWER(TRIM(owner_name))
                    =
                    LOWER(TRIM(?))

                AND
                    LOWER(TRIM(platform_name))
                    =
                    LOWER(TRIM(?))

                AND
                    LOWER(TRIM(account_name))
                    =
                    LOWER(TRIM(?))

                LIMIT 1
                """,
                (
                    owner_name,
                    platform_name,
                    account_name,
                ),
            ).fetchone()

        if row is None:

            return None

        return self._row_to_account(
            row
        )

    # =====================================================
    # GET ACCOUNT
    # =====================================================

    def get_account(
        self,
        account_id,
    ):

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT *
                FROM accounts
                WHERE account_id = ?
                LIMIT 1
                """,
                (
                    account_id,
                ),
            ).fetchone()

        if row is None:

            return None

        return self._row_to_account(
            row
        )

    # =====================================================
    # LIST ACCOUNTS
    # =====================================================

    def list_accounts(
        self,
        active_only=False,
    ):

        query = """
            SELECT *
            FROM accounts
        """

        parameters = ()

        if active_only:

            query += """
                WHERE is_active = 1
            """

        query += """
            ORDER BY
                owner_name,
                platform_name,
                account_name
        """

        with self._connect() as connection:

            rows = connection.execute(
                query,
                parameters,
            ).fetchall()

        return [
            self._row_to_account(
                row
            )
            for row in rows
        ]

    # =====================================================
    # COUNT ACCOUNTS
    # =====================================================

    def count_accounts(self):

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM accounts
                """
            ).fetchone()

        return int(
            row["total"]
        )

    # =====================================================
    # ROW CONVERSION
    # =====================================================

    @staticmethod
    def _row_to_account(
        row,
    ):

        return PortfolioAccount(
            account_id=row[
                "account_id"
            ],

            owner_name=row[
                "owner_name"
            ],

            platform_name=row[
                "platform_name"
            ],

            account_name=row[
                "account_name"
            ],

            external_account_reference=row[
                "external_account_reference"
            ],

            is_active=bool(
                row[
                    "is_active"
                ]
            ),

            created_at=datetime.fromisoformat(
                row[
                    "created_at"
                ]
            ),

            updated_at=datetime.fromisoformat(
                row[
                    "updated_at"
                ]
            ),
        )