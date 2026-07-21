from dataclasses import dataclass, field
from typing import List

from models.account import PortfolioAccount
from models.stored_holding import StoredHolding

from services.portfolio_database import PortfolioDatabase
from services.holdings_database import HoldingsDatabase
from services.holdings_sync_service import HoldingsSyncService

from services.holdings_import_preview import (
    HoldingsImportPreviewService,
)


@dataclass
class PortfolioImportResult:
    """
    Result of one validated portfolio import operation.
    """

    success: bool

    account_id: str = ""

    account_display_name: str = ""

    mode: str = ""

    incoming_count: int = 0

    added_count: int = 0

    updated_count: int = 0

    removed_count: int = 0

    unchanged_count: int = 0

    errors: List[str] = field(
        default_factory=list
    )


@dataclass
class PortfolioImportPreviewResult:
    """
    Read-only result describing what an import would do.

    No database changes are made by preview operations.
    """

    success: bool

    account_id: str = ""

    account_display_name: str = ""

    mode: str = ""

    incoming_count: int = 0

    added_count: int = 0

    updated_count: int = 0

    removed_count: int = 0

    unchanged_count: int = 0

    added: List = field(
        default_factory=list
    )

    updated: List = field(
        default_factory=list
    )

    removed: List = field(
        default_factory=list
    )

    unchanged: List = field(
        default_factory=list
    )

    errors: List[str] = field(
        default_factory=list
    )


class PortfolioImportService:
    """
    Bridge between PMPH's Universal Holdings Reader /
    Validator and the persistent portfolio database.

    Responsibilities:

    - Resolve or create the selected portfolio account.
    - Convert validated universal holdings into StoredHolding.
    - Reject invalid/unvalidated rows.
    - Preview FULL/PARTIAL import impact without database writes.
    - Synchronize holdings in FULL or PARTIAL mode.
    - Preserve source-file traceability.

    This service intentionally contains no Streamlit code.
    """

    def __init__(
        self,
        database_path="data/pmph_portfolio.db",
    ):

        self.database_path = database_path

        self.portfolio_database = (
            PortfolioDatabase(
                database_path
            )
        )

        self.holdings_database = (
            HoldingsDatabase(
                database_path
            )
        )

        self.sync_service = (
            HoldingsSyncService(
                self.holdings_database
            )
        )

        self.preview_service = (
            HoldingsImportPreviewService(
                self.holdings_database
            )
        )

    # =====================================================
    # ACCOUNT MANAGEMENT
    # =====================================================

    def get_accounts(
        self,
        active_only=True,
    ):

        return (
            self.portfolio_database.list_accounts(
                active_only=active_only
            )
        )

    def get_or_create_account(
        self,
        owner_name,
        platform_name,
        account_name,
        external_account_reference=None,
    ):

        account = PortfolioAccount(
            owner_name=owner_name,
            platform_name=platform_name,
            account_name=account_name,
            external_account_reference=(
                external_account_reference
            ),
        )

        return (
            self.portfolio_database.save_account(
                account
            )
        )

    # =====================================================
    # MODE VALIDATION
    # =====================================================

    @staticmethod
    def _normalize_mode(
        mode,
    ):

        return (
            str(mode)
            .strip()
            .upper()
        )

    @staticmethod
    def _mode_is_valid(
        normalized_mode,
    ):

        return (
            normalized_mode
            in {
                HoldingsSyncService.FULL,
                HoldingsSyncService.PARTIAL,
            }
        )

    # =====================================================
    # SHARED VALIDATED-HOLDING CONVERSION
    # =====================================================

    def _convert_validated_holdings(
        self,
        account,
        validation_results,
        source_file=None,
    ):

        """
        Convert PMPH validation results into StoredHolding
        objects.

        This conversion is shared by both preview and actual
        import so both paths interpret holdings identically.

        Returns:

            stored_holdings,
            conversion_errors
        """

        stored_holdings = []

        conversion_errors = []

        for validation_result in (
            validation_results
        ):

            if not validation_result.is_valid:

                symbol = (
                    validation_result
                    .holding
                    .symbol
                )

                conversion_errors.append(
                    (
                        f"{symbol}: "
                        "holding failed financial validation."
                    )
                )

                continue

            holding = (
                validation_result.holding
            )

            try:

                stored_holding = (
                    StoredHolding(
                        account_id=(
                            account.account_id
                        ),

                        symbol=(
                            holding.symbol
                            or ""
                        ),

                        name=(
                            holding.name
                            or holding.symbol
                            or ""
                        ),

                        isin=(
                            holding.isin
                            or ""
                        ),

                        asset_type=(
                            holding.asset_type
                            or ""
                        ),

                        quantity=float(
                            holding.quantity
                            or 0.0
                        ),

                        average_price=float(
                            holding.average_price
                            or 0.0
                        ),

                        current_price=float(
                            holding.current_price
                            or 0.0
                        ),

                        invested_value=float(
                            holding.invested_value
                            or 0.0
                        ),

                        current_value=float(
                            holding.current_value
                            or 0.0
                        ),

                        profit_loss=float(
                            holding.profit_loss
                            or 0.0
                        ),

                        profit_loss_percent=float(
                            holding.profit_loss_percent
                            or 0.0
                        ),

                        source_file=(
                            source_file
                        ),
                    )
                )

                errors = (
                    stored_holding.validate()
                )

                if errors:

                    conversion_errors.append(
                        (
                            f"{holding.symbol}: "
                            + "; ".join(
                                errors
                            )
                        )
                    )

                    continue

                stored_holdings.append(
                    stored_holding
                )

            except Exception as error:

                conversion_errors.append(
                    (
                        f"{holding.symbol}: "
                        f"{error}"
                    )
                )

        return (
            stored_holdings,
            conversion_errors,
        )

    # =====================================================
    # PREVIEW VALIDATED HOLDINGS
    # =====================================================

    def preview_validated_holdings(
        self,
        account,
        validation_results,
        mode,
        source_file=None,
    ):

        """
        Calculate the impact of an import without changing
        the database.

        Preview and actual import use the exact same
        validated-holding conversion logic.
        """

        if account is None:

            return (
                PortfolioImportPreviewResult(
                    success=False,
                    errors=[
                        "A portfolio account is required."
                    ],
                )
            )

        normalized_mode = (
            self._normalize_mode(
                mode
            )
        )

        if not self._mode_is_valid(
            normalized_mode
        ):

            return (
                PortfolioImportPreviewResult(
                    success=False,

                    account_id=(
                        account.account_id
                    ),

                    account_display_name=(
                        account.display_name()
                    ),

                    mode=(
                        normalized_mode
                    ),

                    errors=[
                        (
                            "Import mode must be "
                            "FULL or PARTIAL."
                        )
                    ],
                )
            )

        (
            stored_holdings,
            conversion_errors,
        ) = self._convert_validated_holdings(
            account=account,
            validation_results=(
                validation_results
            ),
            source_file=source_file,
        )

        # -------------------------------------------------
        # FULL preview must be blocked if any incoming row
        # failed conversion.
        #
        # This mirrors actual FULL import safety exactly.
        # -------------------------------------------------

        if (
            normalized_mode
            == HoldingsSyncService.FULL
            and conversion_errors
        ):

            return (
                PortfolioImportPreviewResult(
                    success=False,

                    account_id=(
                        account.account_id
                    ),

                    account_display_name=(
                        account.display_name()
                    ),

                    mode=(
                        normalized_mode
                    ),

                    incoming_count=len(
                        validation_results
                    ),

                    errors=(
                        conversion_errors
                    ),
                )
            )

        if not stored_holdings:

            return (
                PortfolioImportPreviewResult(
                    success=False,

                    account_id=(
                        account.account_id
                    ),

                    account_display_name=(
                        account.display_name()
                    ),

                    mode=(
                        normalized_mode
                    ),

                    incoming_count=0,

                    errors=(
                        conversion_errors
                        or [
                            (
                                "No validated holdings are "
                                "available for preview."
                            )
                        ]
                    ),
                )
            )

        try:

            impact = (
                self.preview_service.preview(
                    account_id=(
                        account.account_id
                    ),

                    incoming_holdings=(
                        stored_holdings
                    ),

                    mode=(
                        normalized_mode
                    ),
                )
            )

        except Exception as error:

            return (
                PortfolioImportPreviewResult(
                    success=False,

                    account_id=(
                        account.account_id
                    ),

                    account_display_name=(
                        account.display_name()
                    ),

                    mode=(
                        normalized_mode
                    ),

                    incoming_count=len(
                        stored_holdings
                    ),

                    errors=(
                        conversion_errors
                        + [
                            str(error)
                        ]
                    ),
                )
            )

        return (
            PortfolioImportPreviewResult(
                success=(
                    not conversion_errors
                ),

                account_id=(
                    account.account_id
                ),

                account_display_name=(
                    account.display_name()
                ),

                mode=(
                    normalized_mode
                ),

                incoming_count=len(
                    stored_holdings
                ),

                added_count=(
                    impact.added_count
                ),

                updated_count=(
                    impact.updated_count
                ),

                removed_count=(
                    impact.removed_count
                ),

                unchanged_count=(
                    impact.unchanged_count
                ),

                added=(
                    impact.added
                ),

                updated=(
                    impact.updated
                ),

                removed=(
                    impact.removed
                ),

                unchanged=(
                    impact.unchanged
                ),

                errors=(
                    conversion_errors
                ),
            )
        )

    # =====================================================
    # IMPORT VALIDATED HOLDINGS
    # =====================================================

    def import_validated_holdings(
        self,
        account,
        validation_results,
        mode,
        source_file=None,
    ):

        if account is None:

            return (
                PortfolioImportResult(
                    success=False,

                    errors=[
                        (
                            "A portfolio account "
                            "is required."
                        )
                    ],
                )
            )

        normalized_mode = (
            self._normalize_mode(
                mode
            )
        )

        if not self._mode_is_valid(
            normalized_mode
        ):

            return (
                PortfolioImportResult(
                    success=False,

                    account_id=(
                        account.account_id
                    ),

                    account_display_name=(
                        account.display_name()
                    ),

                    mode=(
                        normalized_mode
                    ),

                    errors=[
                        (
                            "Import mode must be "
                            "FULL or PARTIAL."
                        )
                    ],
                )
            )

        (
            stored_holdings,
            conversion_errors,
        ) = self._convert_validated_holdings(
            account=account,
            validation_results=(
                validation_results
            ),
            source_file=source_file,
        )

        # -------------------------------------------------
        # Never perform a FULL sync if any row failed.
        #
        # This protects existing holdings from accidental
        # deletion caused by incomplete conversion.
        # -------------------------------------------------

        if (
            normalized_mode
            == HoldingsSyncService.FULL
            and conversion_errors
        ):

            return (
                PortfolioImportResult(
                    success=False,

                    account_id=(
                        account.account_id
                    ),

                    account_display_name=(
                        account.display_name()
                    ),

                    mode=(
                        normalized_mode
                    ),

                    incoming_count=len(
                        validation_results
                    ),

                    errors=(
                        conversion_errors
                    ),
                )
            )

        if not stored_holdings:

            return (
                PortfolioImportResult(
                    success=False,

                    account_id=(
                        account.account_id
                    ),

                    account_display_name=(
                        account.display_name()
                    ),

                    mode=(
                        normalized_mode
                    ),

                    incoming_count=0,

                    errors=(
                        conversion_errors
                        or [
                            (
                                "No validated holdings are "
                                "available for import."
                            )
                        ]
                    ),
                )
            )

        # -------------------------------------------------
        # Synchronize with persistent database
        # -------------------------------------------------

        sync_result = (
            self.sync_service.synchronize(
                account_id=(
                    account.account_id
                ),

                incoming_holdings=(
                    stored_holdings
                ),

                mode=(
                    normalized_mode
                ),
            )
        )

        all_errors = (
            conversion_errors
            + sync_result.errors
        )

        return (
            PortfolioImportResult(
                success=(
                    sync_result.success
                    and not all_errors
                ),

                account_id=(
                    account.account_id
                ),

                account_display_name=(
                    account.display_name()
                ),

                mode=(
                    normalized_mode
                ),

                incoming_count=(
                    sync_result.incoming_count
                ),

                added_count=(
                    sync_result.added_count
                ),

                updated_count=(
                    sync_result.updated_count
                ),

                removed_count=(
                    sync_result.removed_count
                ),

                unchanged_count=(
                    sync_result.unchanged_count
                ),

                errors=(
                    all_errors
                ),
            )
        )

    # =====================================================
    # PORTFOLIO READBACK
    # =====================================================

    def get_account_holdings(
        self,
        account_id,
    ):

        return (
            self.holdings_database.list_holdings(
                account_id
            )
        )

    def get_all_holdings(
        self,
    ):

        return (
            self.holdings_database.list_holdings()
        )