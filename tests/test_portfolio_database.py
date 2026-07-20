import os

from models.account import PortfolioAccount
from services.portfolio_database import PortfolioDatabase


TEST_DATABASE = (
    r"D:\PMPH\data\test_pmph_portfolio.db"
)


def main():

    print("=" * 72)
    print("PMPH PORTFOLIO DATABASE TEST")
    print("=" * 72)

    # Always start the test with a clean database.

    if os.path.exists(
        TEST_DATABASE
    ):

        os.remove(
            TEST_DATABASE
        )

    database = PortfolioDatabase(
        TEST_DATABASE
    )

    print()
    print(
        "Database Created:",
        os.path.exists(
            TEST_DATABASE
        )
    )

    # =====================================================
    # CREATE TEST ACCOUNTS
    # =====================================================

    account_1 = PortfolioAccount(
        owner_name="Suraj",
        platform_name="Groww",
        account_name="Main Portfolio",
    )

    account_2 = PortfolioAccount(
        owner_name="Family Member",
        platform_name="Zerodha",
        account_name="Investment Account",
    )

    account_3 = PortfolioAccount(
        owner_name="Family Member",
        platform_name="ProStocks",
        account_name="Investment Account",
    )

    database.save_account(
        account_1
    )

    database.save_account(
        account_2
    )

    database.save_account(
        account_3
    )

    print()
    print(
        "Accounts Saved:",
        database.count_accounts()
    )

    # =====================================================
    # DUPLICATE-SAFETY TEST
    # =====================================================

    duplicate = PortfolioAccount(
        owner_name="Suraj",
        platform_name="Groww",
        account_name="Main Portfolio",
    )

    returned_account = (
        database.save_account(
            duplicate
        )
    )

    print()
    print(
        "Accounts After Duplicate Attempt:",
        database.count_accounts()
    )

    print(
        "Duplicate Returned Existing ID:",
        returned_account.account_id
        == account_1.account_id
    )

    # =====================================================
    # READ BACK FROM DATABASE
    # =====================================================

    print()
    print("-" * 72)
    print("SAVED ACCOUNTS")
    print("-" * 72)

    accounts = (
        database.list_accounts()
    )

    for account in accounts:

        print()
        print(
            "Account ID:",
            account.account_id
        )

        print(
            "Display Name:",
            account.display_name()
        )

        print(
            "Active:",
            account.is_active
        )

    # =====================================================
    # LOOKUP TEST
    # =====================================================

    found = database.find_account(
        owner_name="suraj",
        platform_name="groww",
        account_name="main portfolio",
    )

    print()
    print("-" * 72)

    print(
        "Case-Insensitive Lookup:",
        (
            "PASS"
            if found is not None
            else "FAIL"
        )
    )

    print(
        "Duplicate Prevention:",
        (
            "PASS"
            if database.count_accounts()
            == 3
            else "FAIL"
        )
    )

    print()
    print("=" * 72)
    print("DATABASE TEST COMPLETE")
    print("=" * 72)


if __name__ == "__main__":

    main()