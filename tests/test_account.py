from models.account import PortfolioAccount


def main():

    print("=" * 70)
    print("PMPH PORTFOLIO ACCOUNT MODEL TEST")
    print("=" * 70)

    accounts = [

        PortfolioAccount(
            owner_name="Suraj",
            platform_name="Groww",
            account_name="Main Portfolio",
        ),

        PortfolioAccount(
            owner_name="Family Member",
            platform_name="Zerodha",
            account_name="Investment Account",
        ),

        PortfolioAccount(
            owner_name="Family Member",
            platform_name="ProStocks",
            account_name="Investment Account",
        ),
    ]

    for account in accounts:

        print()
        print("-" * 70)

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

        errors = account.validate()

        print(
            "Validation:",
            (
                "PASS"
                if not errors
                else "FAIL"
            )
        )

        if errors:

            for error in errors:

                print(
                    " -",
                    error
                )

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":

    main()