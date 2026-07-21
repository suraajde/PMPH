import os
from dataclasses import dataclass

from services.portfolio_import_service import (
    PortfolioImportService,
)


TEST_DATABASE = (
    r"D:\PMPH\data\test_portfolio_import_bridge.db"
)


# =========================================================
# TEST OBJECTS
#
# These imitate the output structure produced by the
# Universal Holdings Reader + Holdings Validator.
# =========================================================

@dataclass
class TestHolding:

    symbol: str
    name: str
    isin: str
    asset_type: str

    quantity: float
    average_price: float
    current_price: float

    invested_value: float
    current_value: float

    profit_loss: float
    profit_loss_percent: float


@dataclass
class TestValidationResult:

    holding: TestHolding
    is_valid: bool = True


def make_validation_result(
    symbol,
    isin,
    quantity,
    average_price,
    current_price,
):

    invested_value = (
        quantity
        * average_price
    )

    current_value = (
        quantity
        * current_price
    )

    profit_loss = (
        current_value
        - invested_value
    )

    if invested_value:

        profit_loss_percent = (
            profit_loss
            / invested_value
            * 100
        )

    else:

        profit_loss_percent = 0.0

    holding = TestHolding(
        symbol=symbol,
        name=f"{symbol} Holding",
        isin=isin,
        asset_type="ETF",

        quantity=quantity,
        average_price=average_price,
        current_price=current_price,

        invested_value=invested_value,
        current_value=current_value,

        profit_loss=profit_loss,
        profit_loss_percent=(
            profit_loss_percent
        ),
    )

    return TestValidationResult(
        holding=holding,
        is_valid=True,
    )


def main():

    print("=" * 76)
    print("PMPH PORTFOLIO IMPORT BRIDGE TEST")
    print("=" * 76)

    if os.path.exists(
        TEST_DATABASE
    ):

        os.remove(
            TEST_DATABASE
        )

    service = (
        PortfolioImportService(
            TEST_DATABASE
        )
    )

    # =====================================================
    # CREATE / RESOLVE ACCOUNT
    # =====================================================

    account = (
        service.get_or_create_account(
            owner_name="Test Owner",
            platform_name="Test Broker",
            account_name="Main Portfolio",
        )
    )

    duplicate_account = (
        service.get_or_create_account(
            owner_name="test owner",
            platform_name="test broker",
            account_name="main portfolio",
        )
    )

    print()
    print(
        "Account:",
        account.display_name()
    )

    print(
        "Account Duplicate Prevention:",
        (
            "PASS"
            if (
                account.account_id
                == duplicate_account.account_id
            )
            else "FAIL"
        )
    )

    # =====================================================
    # FIRST FULL IMPORT
    # =====================================================

    first_statement = [

        make_validation_result(
            "MIDCAP",
            "BRIDGEISIN001",
            100,
            20,
            22,
        ),

        make_validation_result(
            "SMALLCAP",
            "BRIDGEISIN002",
            200,
            40,
            44,
        ),

        make_validation_result(
            "GOLDBEES",
            "BRIDGEISIN003",
            50,
            100,
            110,
        ),
    ]

    first_result = (
        service.import_validated_holdings(
            account=account,
            validation_results=(
                first_statement
            ),
            mode="FULL",
            source_file=(
                "first_statement.xlsx"
            ),
        )
    )

    print()
    print("FIRST FULL IMPORT")
    print("-" * 76)

    print(
        "Success:",
        first_result.success
    )

    print(
        "Added:",
        first_result.added_count
    )

    print(
        "Updated:",
        first_result.updated_count
    )

    print(
        "Removed:",
        first_result.removed_count
    )

    # =====================================================
    # SECOND FULL IMPORT
    #
    # MIDCAP updated
    # SMALLCAP updated
    # GOLDBEES sold/disappeared
    # NEWETF added
    # =====================================================

    second_statement = [

        make_validation_result(
            "MIDCAP",
            "BRIDGEISIN001",
            125,
            20.50,
            24,
        ),

        make_validation_result(
            "SMALLCAP",
            "BRIDGEISIN002",
            220,
            41,
            46,
        ),

        make_validation_result(
            "NEWETF",
            "BRIDGEISIN004",
            75,
            50,
            55,
        ),
    ]

    second_result = (
        service.import_validated_holdings(
            account=account,
            validation_results=(
                second_statement
            ),
            mode="FULL",
            source_file=(
                "second_statement.xlsx"
            ),
        )
    )

    print()
    print("SECOND FULL IMPORT")
    print("-" * 76)

    print(
        "Success:",
        second_result.success
    )

    print(
        "Added:",
        second_result.added_count
    )

    print(
        "Updated:",
        second_result.updated_count
    )

    print(
        "Removed:",
        second_result.removed_count
    )

    # =====================================================
    # READ BACK
    # =====================================================

    holdings = (
        service.get_account_holdings(
            account.account_id
        )
    )

    symbols = {
        holding.symbol
        for holding
        in holdings
    }

    print()
    print("PERSISTED PORTFOLIO")
    print("-" * 76)

    for holding in holdings:

        print(
            holding.symbol,
            "->",
            holding.quantity,
            "->",
            holding.source_file
        )

    print()
    print("-" * 76)

    print(
        "First Import:",
        (
            "PASS"
            if (
                first_result.success
                and first_result.added_count
                == 3
            )
            else "FAIL"
        )
    )

    print(
        "Second Import Synchronization:",
        (
            "PASS"
            if (
                second_result.success
                and second_result.added_count
                == 1
                and second_result.updated_count
                == 2
                and second_result.removed_count
                == 1
            )
            else "FAIL"
        )
    )

    print(
        "Sold Holding Removed:",
        (
            "PASS"
            if "GOLDBEES"
            not in symbols
            else "FAIL"
        )
    )

    print(
        "Expected Current Portfolio:",
        (
            "PASS"
            if symbols
            == {
                "MIDCAP",
                "SMALLCAP",
                "NEWETF",
            }
            else "FAIL"
        )
    )

    print(
        "Persistent Holding Count:",
        (
            "PASS"
            if len(
                holdings
            ) == 3
            else "FAIL"
        )
    )

    print()
    print("=" * 76)
    print("PORTFOLIO IMPORT BRIDGE TEST COMPLETE")
    print("=" * 76)


if __name__ == "__main__":

    main()