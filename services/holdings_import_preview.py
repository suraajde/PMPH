from dataclasses import dataclass, field
from typing import List


@dataclass
class HoldingImpact:
    action: str
    security_key: str
    symbol: str
    isin: str
    old_quantity: float = 0.0
    new_quantity: float = 0.0


@dataclass
class ImportImpactPreview:
    account_id: str
    mode: str

    added: List[HoldingImpact] = field(
        default_factory=list
    )

    updated: List[HoldingImpact] = field(
        default_factory=list
    )

    removed: List[HoldingImpact] = field(
        default_factory=list
    )

    unchanged: List[HoldingImpact] = field(
        default_factory=list
    )

    @property
    def added_count(self):
        return len(self.added)

    @property
    def updated_count(self):
        return len(self.updated)

    @property
    def removed_count(self):
        return len(self.removed)

    @property
    def unchanged_count(self):
        return len(self.unchanged)


class HoldingsImportPreviewService:
    """
    Read-only preview of the effect an import would have.

    This service NEVER changes the database.
    """

    FULL = "FULL"
    PARTIAL = "PARTIAL"

    def __init__(
        self,
        holdings_database,
    ):
        self.holdings_database = (
            holdings_database
        )

    def preview(
        self,
        account_id,
        incoming_holdings,
        mode,
    ):

        normalized_mode = (
            str(mode)
            .strip()
            .upper()
        )

        if normalized_mode not in {
            self.FULL,
            self.PARTIAL,
        }:
            raise ValueError(
                "Preview mode must be FULL or PARTIAL."
            )

        preview = ImportImpactPreview(
            account_id=account_id,
            mode=normalized_mode,
        )

        existing_holdings = (
            self.holdings_database
            .list_holdings(
                account_id
            )
        )

        existing_by_key = {
            holding.security_key():
                holding
            for holding
            in existing_holdings
        }

        incoming_by_key = {
            holding.security_key():
                holding
            for holding
            in incoming_holdings
        }

        for (
            security_key,
            incoming,
        ) in incoming_by_key.items():

            existing = (
                existing_by_key.get(
                    security_key
                )
            )

            if existing is None:

                preview.added.append(
                    HoldingImpact(
                        action="ADD",
                        security_key=security_key,
                        symbol=incoming.symbol,
                        isin=incoming.isin,
                        old_quantity=0.0,
                        new_quantity=(
                            incoming.quantity
                        ),
                    )
                )

                continue

            if self._holding_changed(
                existing,
                incoming,
            ):

                preview.updated.append(
                    HoldingImpact(
                        action="UPDATE",
                        security_key=security_key,
                        symbol=incoming.symbol,
                        isin=incoming.isin,
                        old_quantity=(
                            existing.quantity
                        ),
                        new_quantity=(
                            incoming.quantity
                        ),
                    )
                )

            else:

                preview.unchanged.append(
                    HoldingImpact(
                        action="UNCHANGED",
                        security_key=security_key,
                        symbol=incoming.symbol,
                        isin=incoming.isin,
                        old_quantity=(
                            existing.quantity
                        ),
                        new_quantity=(
                            incoming.quantity
                        ),
                    )
                )

        if normalized_mode == self.FULL:

            incoming_keys = set(
                incoming_by_key.keys()
            )

            for existing in (
                existing_holdings
            ):

                security_key = (
                    existing.security_key()
                )

                if (
                    security_key
                    not in incoming_keys
                ):

                    preview.removed.append(
                        HoldingImpact(
                            action="REMOVE",
                            security_key=(
                                security_key
                            ),
                            symbol=(
                                existing.symbol
                            ),
                            isin=(
                                existing.isin
                            ),
                            old_quantity=(
                                existing.quantity
                            ),
                            new_quantity=0.0,
                        )
                    )

        return preview

    @staticmethod
    def _holding_changed(
        existing,
        incoming,
    ):

        text_fields = [
            "symbol",
            "name",
            "isin",
            "asset_type",
        ]

        for field_name in text_fields:

            old_value = (
                getattr(
                    existing,
                    field_name,
                )
                or ""
            )

            new_value = (
                getattr(
                    incoming,
                    field_name,
                )
                or ""
            )

            if (
                str(old_value).strip()
                !=
                str(new_value).strip()
            ):
                return True

        numeric_fields = [
            "quantity",
            "average_price",
            "current_price",
            "invested_value",
            "current_value",
            "profit_loss",
            "profit_loss_percent",
        ]

        for field_name in numeric_fields:

            old_value = float(
                getattr(
                    existing,
                    field_name,
                )
            )

            new_value = float(
                getattr(
                    incoming,
                    field_name,
                )
            )

            if abs(
                old_value
                - new_value
            ) > 0.000001:
                return True

        return False