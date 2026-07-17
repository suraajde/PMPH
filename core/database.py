import sqlite3
from config import DATABASE_PATH


class Database:

    def __init__(self):
        self.connection = None

    def connect(self):
        self.connection = sqlite3.connect(DATABASE_PATH)
        return self.connection

    def close(self):
        if self.connection:
            self.connection.close()