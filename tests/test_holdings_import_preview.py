import os

from models.account import PortfolioAccount
from models.stored_holding import StoredHolding

from services.portfolio_database import (
    PortfolioDatabase,
)

from services.holdings_database import (
    HoldingsDatabase,
)

from services.holdings_import_preview import (
    HoldingsImportPreviewService,
)


TEST_DATABASE = (
    r"D:\PMPH\data\test_import_preview.db"
)


def make_holding(
    account_id,
    symbol,
    isin,
    quantity,
):

    price = 100.0

    return StoredHolding(
        account_id=account_id,
        symbol=symbol,
        name=symbol,
        isin=isin,
        asset_type="ETF",
        quantity=quantity,
        average_price=price,
        current_price=price,
        invested_value=(
            quantity * price
        ),
        current_value=(
            quantity * price
        ),
        profit_loss=0.0,
        profit_loss_percent=0.0,
    )


def main():

    print("=" * 72)
    print("PMPH PRE-IMPORT IMPACT PREVIEW TEST")
    print("=" * 72)

    if os.path.exists(
        TEST_DATABASE
    ):
        os.remove(
            TEST_DATABASE
        )

    portfolio_database = (
        PortfolioDatabase(
            TEST_DATABASE
        )
    )

    account = (
        portfolio_database.save_account(
            PortfolioAccount(
                owner_name="Test Owner",
                platform_name="Test Broker",
                account_name="Main Portfolio",
            )
        )
    )

    holdings_database = (
        HoldingsDatabase(
            TEST_DATABASE
        )
    )

    # Existing portfolio:
    #
    # MIDCAP   100
    # SMALLCAP 200
    # GOLDBEES 50

    holdings_database.save_holding(
        make_holding(
            account.account_id,
            "MIDCAP",
            "PREVIEW001",
            100,
        )
    )

    holdings_database.save_holding(
        make_holding(
            account.account_id,
            "SMALLCAP",
            "PREVIEW002",
            200,
        )
    )

    holdings_database.save_holding(
        make_holding(
            account.account_id,
            "GOLDBEES",
            "PREVIEW003",
            50,
        )
    )

    # Incoming statement:
    #
    # MIDCAP   125 -> UPDATE
    # SMALLCAP 200 -> UNCHANGED
    # NEWETF    75 -> ADD
    #
    # GOLDBEES absent:
    # FULL    -> REMOVE
    # PARTIAL -> KEEP

    incoming = [
        make_holding(
            account.account_id,
            "MIDCAP",
            "PREVIEW001",
            125,
        ),

        make_holding(
            account.account_id,
            "SMALLCAP",
            "PREVIEW002",
            200,
        ),

        make_holding(
            account.account_id,
            "NEWETF",
            "PREVIEW004",
            75,
        ),
    ]

    service = (
        HoldingsImportPreviewService(
            holdings_database
        )
    )

    full_preview = (
        service.preview(
            account_id=(
                account.account_id
            ),
            incoming_holdings=incoming,
            mode="FULL",
        )
    )

    partial_preview = (
        service.preview(
            account_id=(
                account.account_id
            ),
            incoming_holdings=incoming,
            mode="PARTIAL",
        )
    )

    print()
    print("FULL PREVIEW")
    print("-" * 72)

    print(
        "Added:",
        full_preview.added_count
    )

    print(
        "Updated:",
        full_preview.updated_count
    )

    print(
        "Removed:",
        full_preview.removed_count
    )

    print(
        "Unchanged:",
        full_preview.unchanged_count
    )

    print()
    print("REMOVALS")

    for item in (
        full_preview.removed
    ):
        print(
            item.symbol,
            "->",
            item.old_quantity,
        )

    print()
    print("PARTIAL PREVIEW")
    print("-" * 72)

    print(
        "Added:",
        partial_preview.added_count
    )

    print(
        "Updated:",
        partial_preview.updated_count
    )

    print(
        "Removed:",
        partial_preview.removed_count
    )

    print(
        "Unchanged:",
        partial_preview.unchanged_count
    )

    print()
    print("-" * 72)

    print(
        "FULL Add Detection:",
        (
            "PASS"
            if full_preview.added_count
            == 1
            else "FAIL"
        )
    )

    print(
        "FULL Update Detection:",
        (
            "PASS"
            if full_preview.updated_count
            == 1
            else "FAIL"
        )
    )

    print(
        "FULL Removal Detection:",
        (
            "PASS"
            if (
                full_preview.removed_count
                == 1
                and full_preview.removed[
                    0
                ].symbol
                == "GOLDBEES"
            )
            else "FAIL"
        )
    )

    print(
        "Unchanged Detection:",
        (
            "PASS"
            if full_preview.unchanged_count
            == 1
            else "FAIL"
        )
    )

    print(
        "PARTIAL Removal Protection:",
        (
            "PASS"
            if partial_preview.removed_count
            == 0
            else "FAIL"
        )
    )

    print()
    print("=" * 72)
    print("PRE-IMPORT PREVIEW TEST COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()