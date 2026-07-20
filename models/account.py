from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class PortfolioAccount:
    """
    Represents one investment account inside PMPH.

    Examples:

    Owner: Suraj
    Platform: Groww
    Account Name: Main Portfolio

    Owner: Wife
    Platform: Zerodha
    Account Name: Kite / Coin

    Owner: Daughter
    Platform: ProStocks
    Account Name: Investment Account
    """

    owner_name: str

    platform_name: str

    account_name: str

    account_id: str = field(
        default_factory=lambda: str(
            uuid.uuid4()
        )
    )

    external_account_reference: Optional[str] = None

    is_active: bool = True

    created_at: datetime = field(
        default_factory=datetime.now
    )

    updated_at: datetime = field(
        default_factory=datetime.now
    )

    def display_name(self) -> str:

        parts = [
            self.owner_name,
            self.platform_name,
            self.account_name,
        ]

        return " • ".join(
            part.strip()
            for part in parts
            if part
            and part.strip()
        )

    def validate(self):

        errors = []

        if not self.owner_name.strip():

            errors.append(
                "Owner name is required."
            )

        if not self.platform_name.strip():

            errors.append(
                "Platform/Broker name is required."
            )

        if not self.account_name.strip():

            errors.append(
                "Account name is required."
            )

        return errors