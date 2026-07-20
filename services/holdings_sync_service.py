from dataclasses import dataclass, field
from typing import List

from models.stored_holding import StoredHolding
from services.holdings_database import HoldingsDatabase


@dataclass
class HoldingsSyncResult:
    """
    Summary of one account holdings synchronization.
    """

    account_id: str

    mode: str

    incoming_count: int = 0

    added_count: int = 0

    updated_count: int = 0

    removed_count: int = 0

    unchanged_count: int = 0

    errors: List[str] = field(
        default_factory=list
    )

    @property
    def success(self):

        return not self.errors


class HoldingsSyncService:
    """
    Synchronizes validated holdings with PMPH's
    persistent current-holdings database.

    Modes:

    FULL
        Incoming holdings represent the complete current
        holdings statement for one account.

        - Add new securities
        - Update existing securities
        - Remove securities absent from the new statement

    PARTIAL
        Incoming holdings do not necessarily represent
        the complete account.

        - Add new securities
        - Update existing securities
        - NEVER remove absent securities
    """

    FULL = "FULL"

    PARTIAL = "PARTIAL"

    def __init__(
        self,
        holdings_database: HoldingsDatabase,
    ):

        self.holdings_database = (
            holdings_database
        )

    # =====================================================
    # PUBLIC SYNCHRONIZATION
    # =====================================================

    def synchronize(
        self,
        account_id,
        incoming_holdings,
        mode=PARTIAL,
    ):

        normalized_mode = (
            str(
                mode
            )
            .strip()
            .upper()
        )

        if normalized_mode not in {
            self.FULL,
            self.PARTIAL,
        }:

            raise ValueError(
                "Synchronization mode must be "
                "FULL or PARTIAL."
            )

        result = HoldingsSyncResult(
            account_id=account_id,
            mode=normalized_mode,
            incoming_count=len(
                incoming_holdings
            ),
        )

        # -------------------------------------------------
        # Safety validation before changing database
        # -------------------------------------------------

        prepared_holdings = (
            self._prepare_holdings(
                account_id=account_id,
                incoming_holdings=incoming_holdings,
                result=result,
            )
        )

        if result.errors:

            return result

        # -------------------------------------------------
        # Current database snapshot
        # -------------------------------------------------

        existing_holdings = (
            self.holdings_database.list_holdings(
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
            in prepared_holdings
        }

        # -------------------------------------------------
        # Add / update incoming securities
        # -------------------------------------------------

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

                self.holdings_database.save_holding(
                    incoming
                )

                result.added_count += 1

                continue

            if self._holding_changed(
                existing,
                incoming
            ):

                self.holdings_database.save_holding(
                    incoming
                )

                result.updated_count += 1

            else:

                result.unchanged_count += 1

        # -------------------------------------------------
        # FULL statement only:
        # remove securities absent from latest statement
        # -------------------------------------------------

        if normalized_mode == self.FULL:

            incoming_keys = set(
                incoming_by_key.keys()
            )

            for existing in existing_holdings:

                if (
                    existing.security_key()
                    not in incoming_keys
                ):

                    deleted = (
                        self.holdings_database.delete_holding(
                            existing.holding_id
                        )
                    )

                    if deleted:

                        result.removed_count += 1

        return result

    # =====================================================
    # PREPARE + VALIDATE INCOMING HOLDINGS
    # =====================================================

    def _prepare_holdings(
        self,
        account_id,
        incoming_holdings,
        result,
    ):

        prepared = []

        seen_keys = set()

        for holding in incoming_holdings:

            # Force every incoming row to the account
            # being synchronized.

            holding.account_id = (
                account_id
            )

            errors = holding.validate()

            if errors:

                result.errors.append(
                    (
                        f"{holding.symbol or holding.isin}: "
                        + "; ".join(
                            errors
                        )
                    )
                )

                continue

            security_key = (
                holding.security_key()
            )

            if security_key in seen_keys:

                result.errors.append(
                    (
                        "Duplicate security in incoming "
                        f"statement: {security_key}"
                    )
                )

                continue

            seen_keys.add(
                security_key
            )

            prepared.append(
                holding
            )

        return prepared

    # =====================================================
    # CHANGE DETECTION
    # =====================================================

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
            "source_file",
        ]

        for field_name in text_fields:

            old_value = (
                getattr(
                    existing,
                    field_name
                )
                or ""
            )

            new_value = (
                getattr(
                    incoming,
                    field_name
                )
                or ""
            )

            if (
                str(
                    old_value
                ).strip()
                !=
                str(
                    new_value
                ).strip()
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
                    field_name
                )
            )

            new_value = float(
                getattr(
                    incoming,
                    field_name
                )
            )

            if abs(
                old_value
                - new_value
            ) > 0.000001:

                return True

        return False