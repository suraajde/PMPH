import os

from services.parsers.prostocks import ProStocksParser


class UniversalImporter:

    def detect_broker(self, file_name):

        file_name = os.path.basename(file_name).lower()

        if "prostocks" in file_name:
            return "ProStocks"

        if "groww" in file_name:
            return "Groww"

        if "zerodha" in file_name:
            return "Zerodha"

        return "Unknown"

    def get_parser(self, broker):

        if broker == "ProStocks":
            return ProStocksParser()

        return None