from models.portfolio import PortfolioHolding


class BaseParser:

    def parse(self, file_path):
        """
        Every broker parser must return
        a list of PortfolioHolding objects.
        """
        raise NotImplementedError(
            "Parser must implement parse()."
        )