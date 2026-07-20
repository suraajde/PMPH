from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class StoredHolding:
    """
    Persistent PMPH holding linked to one portfolio account.
    """

    account_id: str

    symbol: str

    name: str

    asset_type: str

    quantity: float

    average_price: float

    current_price: float

    invested_value: float

    current_value: float

    profit_loss: float

    profit_loss_percent: float

    isin: str = ""

    holding_id: str = field(
        default_factory=lambda: str(
            uuid.uuid4()
        )
    )

    source_file: Optional[str] = None

    imported_at: datetime = field(
        default_factory=datetime.now
    )

    updated_at: datetime = field(
        default_factory=datetime.now
    )

    def security_key(self):

        cleaned_isin = (
            self.isin
            or ""
        ).strip().upper()

        if cleaned_isin:

            return (
                f"ISIN:{cleaned_isin}"
            )

        cleaned_symbol = (
            self.symbol
            or ""
        ).strip().upper()

        return (
            f"SYMBOL:{cleaned_symbol}"
        )

    def validate(self):

        errors = []

        if not self.account_id.strip():

            errors.append(
                "Account ID is required."
            )

        if not (
            self.symbol.strip()
            or self.isin.strip()
        ):

            errors.append(
                "Symbol or ISIN is required."
            )

        if self.quantity < 0:

            errors.append(
                "Quantity cannot be negative."
            )

        return errors