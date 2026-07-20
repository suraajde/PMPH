from dataclasses import dataclass


@dataclass
class PortfolioHolding:
    broker: str = ""
    asset_type: str = ""
    symbol: str = ""
    name: str = ""
    isin: str = ""

    quantity: float = 0.0

    average_price: float = 0.0
    current_price: float = 0.0

    invested_value: float = 0.0
    current_value: float = 0.0

    profit_loss: float = 0.0
    profit_loss_percent: float = 0.0