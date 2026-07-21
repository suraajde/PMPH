from pathlib import Path

from services.portfolio_database import (
    PortfolioDatabase,
)

from services.portfolio_import_service import (
    PortfolioImportService,
)


DATABASE_PATH = Path(
    r"D:\PMPH\data\pmph_portfolio.db"
)


def main():

    print("=" * 76)
    print("PMPH LIVE PORTFOLIO PERSISTENCE TEST")
    print("=" * 76)

    print()
    print(
        "Database:",
        DATABASE_PATH,
    )

    print(
        "Database Exists:",
        DATABASE_PATH.exists(),
    )

    # =====================================================
    # DATABASE EXISTENCE CHECK
    # =====================================================

    if not DATABASE_PATH.exists():

        print()
        print("-" * 76)

        print(
            "Database Read: FAIL"
        )

        print(
            "Accounts Persisted: FAIL"
        )

        print(
            "Four Holdings Persisted: FAIL"
        )

        print(
            "Expected Securities Persisted: FAIL"
        )

        print(
            "Holdings Linked To Accounts: FAIL"
        )

        print()
        print(
            "The live PMPH portfolio database "
            "could not be found."
        )

        print()
        print("=" * 76)

        print(
            "LIVE PORTFOLIO PERSISTENCE "
            "TEST COMPLETE"
        )

        print("=" * 76)

        return

    # =====================================================
    # READ ACCOUNTS DIRECTLY FROM SQLITE DATABASE
    # =====================================================

    portfolio_database = (
        PortfolioDatabase(
            str(
                DATABASE_PATH
            )
        )
    )

    accounts = (
        portfolio_database
        .list_accounts()
    )

    # =====================================================
    # READ HOLDINGS DIRECTLY FROM SQLITE DATABASE
    # =====================================================

    import_service = (
        PortfolioImportService(
            str(
                DATABASE_PATH
            )
        )
    )

    holdings = (
        import_service
        .get_all_holdings()
    )

    # =====================================================
    # DISPLAY PERSISTED ACCOUNTS
    # =====================================================

    print()
    print("-" * 76)
    print("PERSISTED ACCOUNTS")
    print("-" * 76)

    if not accounts:

        print()
        print(
            "No persisted accounts found."
        )

    else:

        for account in accounts:

            print()

            print(
                "Account ID:",
                account.account_id,
            )

            print(
                "Account:",
                account.display_name(),
            )

            print(
                "Owner:",
                account.owner_name,
            )

            print(
                "Platform:",
                account.platform_name,
            )

            print(
                "Account Name:",
                account.account_name,
            )

            print(
                "Active:",
                account.is_active,
            )

    print()
    print(
        "Total Accounts:",
        len(
            accounts
        ),
    )

    # =====================================================
    # DISPLAY PERSISTED HOLDINGS
    # =====================================================

    print()
    print("-" * 76)
    print("PERSISTED HOLDINGS")
    print("-" * 76)

    if not holdings:

        print()
        print(
            "No persisted holdings found."
        )

    else:

        for holding in holdings:

            print()

            print(
                "Holding ID:",
                holding.holding_id,
            )

            print(
                "Account ID:",
                holding.account_id,
            )

            print(
                "Asset Type:",
                holding.asset_type,
            )

            print(
                "Symbol:",
                holding.symbol,
            )

            print(
                "Name:",
                holding.name,
            )

            print(
                "ISIN:",
                holding.isin,
            )

            print(
                "Quantity:",
                holding.quantity,
            )

            print(
                "Average Price:",
                holding.average_price,
            )

            print(
                "Current Price:",
                holding.current_price,
            )

            print(
                "Invested Value:",
                holding.invested_value,
            )

            print(
                "Current Value:",
                holding.current_value,
            )

            print(
                "Profit / Loss:",
                holding.profit_loss,
            )

            print(
                "P/L %:",
                holding.profit_loss_percent,
            )

            print(
                "Source File:",
                holding.source_file,
            )

    print()
    print(
        "Total Holdings:",
        len(
            holdings
        ),
    )

    # =====================================================
    # EXPECTED LIVE SECURITIES
    # =====================================================

    persisted_symbols = {

        str(
            holding.symbol
            or ""
        )
        .strip()
        .upper()

        for holding in holdings

        if str(
            holding.symbol
            or ""
        ).strip()
    }

    expected_symbols = {
        "GOLDBEES",
        "HDFCSML250",
        "MIDCAP",
        "SMALLCAP",
    }

    # =====================================================
    # ACCOUNT LINK VALIDATION
    # =====================================================

    account_ids = {

        str(
            account.account_id
        )
        .strip()

        for account in accounts

        if str(
            account.account_id
        ).strip()
    }

    holdings_have_valid_accounts = (

        bool(
            holdings
        )

        and all(

            str(
                holding.account_id
            )
            .strip()

            in account_ids

            for holding in holdings
        )
    )

    # =====================================================
    # EXPECTED ACCOUNT / HOLDING RELATIONSHIPS
    # =====================================================

    account_lookup = {

        str(
            account.account_id
        ).strip():
            account

        for account in accounts
    }

    print()
    print("-" * 76)
    print("ACCOUNT / HOLDING RELATIONSHIPS")
    print("-" * 76)

    for holding in holdings:

        account = (
            account_lookup.get(
                str(
                    holding.account_id
                ).strip()
            )
        )

        if account is None:

            account_name = (
                "ACCOUNT NOT FOUND"
            )

        else:

            account_name = (
                account.display_name()
            )

        print(
            f"{holding.symbol}"
            f" -> "
            f"{account_name}"
        )

    # =====================================================
    # CHECK EXPECTED HOLDING QUANTITIES
    # =====================================================

    quantity_lookup = {

        str(
            holding.symbol
            or ""
        )
        .strip()
        .upper():
            float(
                holding.quantity
                or 0
            )

        for holding in holdings
    }

    expected_quantities = {
        "GOLDBEES": 496.0,
        "HDFCSML250": 131.0,
        "MIDCAP": 8254.0,
        "SMALLCAP": 5683.0,
    }

    quantities_match = all(

        abs(
            quantity_lookup.get(
                symbol,
                -1,
            )
            - expected_quantity
        )
        < 0.000001

        for (
            symbol,
            expected_quantity,
        )
        in (
            expected_quantities.items()
        )
    )

    # =====================================================
    # FINAL CHECKS
    # =====================================================

    database_read_pass = (
        DATABASE_PATH.exists()
    )

    accounts_persisted_pass = (
        len(
            accounts
        )
        >= 2
    )

    four_holdings_pass = (
        len(
            holdings
        )
        == 4
    )

    expected_securities_pass = (
        persisted_symbols
        == expected_symbols
    )

    account_links_pass = (
        holdings_have_valid_accounts
    )

    print()
    print("-" * 76)
    print("FINAL PERSISTENCE CHECKS")
    print("-" * 76)

    print(
        "Database Read:",
        (
            "PASS"
            if database_read_pass
            else "FAIL"
        ),
    )

    print(
        "Accounts Persisted:",
        (
            "PASS"
            if accounts_persisted_pass
            else "FAIL"
        ),
    )

    print(
        "Four Holdings Persisted:",
        (
            "PASS"
            if four_holdings_pass
            else "FAIL"
        ),
    )

    print(
        "Expected Securities Persisted:",
        (
            "PASS"
            if expected_securities_pass
            else "FAIL"
        ),
    )

    print(
        "Expected Quantities Persisted:",
        (
            "PASS"
            if quantities_match
            else "FAIL"
        ),
    )

    print(
        "Holdings Linked To Accounts:",
        (
            "PASS"
            if account_links_pass
            else "FAIL"
        ),
    )

    # =====================================================
    # OVERALL RESULT
    # =====================================================

    all_pass = all(
        [
            database_read_pass,
            accounts_persisted_pass,
            four_holdings_pass,
            expected_securities_pass,
            quantities_match,
            account_links_pass,
        ]
    )

    print()
    print("-" * 76)

    print(
        "OVERALL LIVE PERSISTENCE:",
        (
            "PASS"
            if all_pass
            else "FAIL"
        ),
    )

    print()
    print("=" * 76)

    print(
        "LIVE PORTFOLIO PERSISTENCE "
        "TEST COMPLETE"
    )

    print("=" * 76)


if __name__ == "__main__":

    main()