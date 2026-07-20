from services.holdings_validator import (
    HoldingsValidator,
)

from services.universal_holdings_reader import (
    UniversalHoldingsReader,
)


TEST_FILES = [

    r"D:\PMPH\data\Holdings_prostocks.xlsx",

    r"D:\PMPH\data\holdings-EY0423.xlsx",

]


def main():

    reader = UniversalHoldingsReader()

    validator = HoldingsValidator()

    print("=" * 75)

    print(
        "PMPH UNIVERSAL HOLDINGS VALIDATION TEST"
    )

    print("=" * 75)

    for file_path in TEST_FILES:

        print()
        print("=" * 75)

        print(
            f"FILE: {file_path}"
        )

        print("=" * 75)

        try:

            detection, holdings = (
                reader.read(
                    file_path
                )
            )

        except Exception as error:

            print()

            print(
                "READ FAILED:"
            )

            print(
                str(error)
            )

            continue

        print()

        print(
            "Table Confidence:",
            detection["confidence"]
        )

        print(
            "Holdings Extracted:",
            len(holdings)
        )

        results = (
            validator.validate_holdings(
                holdings
            )
        )

        valid_count = 0

        for result in results:

            holding = result.holding

            print()
            print("-" * 75)

            print(
                "Symbol:",
                holding.symbol
            )

            print(
                "Quantity:",
                holding.quantity
            )

            print(
                "Invested Value:",
                round(
                    holding.invested_value,
                    2
                )
            )

            print(
                "Current Value:",
                round(
                    holding.current_value,
                    2
                )
            )

            print(
                "Profit / Loss:",
                round(
                    holding.profit_loss,
                    2
                )
            )

            print(
                "Validation:",
                (
                    "PASS"
                    if result.is_valid
                    else "FAIL"
                )
            )

            print(
                "Confidence:",
                result.confidence
            )

            print(
                "Checks Passed:",
                result.checks_passed
            )

            print(
                "Checks Failed:",
                result.checks_failed
            )

            if result.warnings:

                print(
                    "Warnings:"
                )

                for warning in (
                    result.warnings
                ):

                    print(
                        " -",
                        warning
                    )

            if result.errors:

                print(
                    "Errors:"
                )

                for error in (
                    result.errors
                ):

                    print(
                        " -",
                        error
                    )

            if result.is_valid:

                valid_count += 1

        print()
        print(
            f"VALIDATED: "
            f"{valid_count}/{len(results)}"
        )

    print()
    print("=" * 75)

    print(
        "VALIDATION TEST COMPLETE"
    )

    print("=" * 75)


if __name__ == "__main__":

    main()