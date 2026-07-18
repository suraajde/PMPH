import sqlite3
from config import DATABASE_PATH


class DatabaseManager:
    """Database manager for PMPH."""

    def __init__(self):
        self.connection = None

    def connect(self):
        """Connect to SQLite database."""
        self.connection = sqlite3.connect(DATABASE_PATH)
        return self.connection

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()

    def create_tables(self):
        """Create all required tables."""

        cursor = self.connection.cursor()

        # ======================================================
        # Holdings
        # ======================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                name TEXT,
                category TEXT,
                quantity REAL,
                average_price REAL,
                current_price REAL,
                broker TEXT
            )
        """)

        # ======================================================
        # Transactions
        # ======================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_date TEXT,
                symbol TEXT,
                transaction_type TEXT,
                quantity REAL,
                price REAL,
                charges REAL,
                broker TEXT
            )
        """)

        # ======================================================
        # SIP Master
        # ======================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sip_master (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                investment_name TEXT,
                sip_amount REAL,
                sip_date INTEGER,
                frequency TEXT,
                active INTEGER
            )
        """)

        # ======================================================
        # Watchlist
        # ======================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                remarks TEXT
            )
        """)

        # ======================================================
        # Fund Master
        # ======================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fund_master (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_code TEXT,
                fund_name TEXT,
                category TEXT
            )
        """)

        # ======================================================
        # ETF Master
        # ======================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS etf_master (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                name TEXT,
                index_name TEXT
            )
        """)

        # ======================================================
        # Application Settings
        # ======================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT
            )
        """)

        self.connection.commit()

    def initialize_database(self):
        """Initialize PMPH database."""
        self.connect()
        self.create_tables()