from services.universal_holdings_reader import (
    UniversalHoldingsReader,
)


# =========================================================
# TEST FILE
# =========================================================

FILE_PATH = (
    r"D:\PMPH\data\holdings-EY0423.xlsx"
)


def main():

    print("=" * 70)
    print("PMPH UNIVERSAL HOLDINGS READER TEST")
    print("=" * 70)

    print()
    print("File:")
    print(FILE_PATH)

    reader = UniversalHoldingsReader()

    # -----------------------------------------------------
    # STEP 1 - Inspect file structure
    # -----------------------------------------------------

    print()
    print("Inspecting file content...")

    detection = reader.inspect(
        FILE_PATH
    )

    print()
    print("-" * 70)
    print("DETECTION RESULT")
    print("-" * 70)

    print(
        "Holdings Table Detected:",
        detection.get(
            "detected",
            False
        )
    )

    print(
        "Confidence:",
        detection.get(
            "confidence",
            "UNKNOWN"
        )
    )

    print(
        "Sheet:",
        detection.get(
            "sheet_name"
        )
    )

    print(
        "Header Row:",
        detection.get(
            "header_row"
        )
    )

    print(
        "Detection Score:",
        detection.get(
            "score",
            0
        )
    )

    print()
    print("Detected Column Mapping")
    print("-" * 70)

    mapping = detection.get(
        "mapping",
        {}
    )

    if mapping:

        for (
            standard_field,
            details
        ) in mapping.items():

            print(
                f"{details['original_name']}"
                f"  ->  "
                f"{standard_field}"
            )

    else:

        print(
            "No universal columns were "
            "confidently mapped."
        )

    # -----------------------------------------------------
    # STEP 2 - Stop safely if table not recognized
    # -----------------------------------------------------

    if not detection.get(
        "detected",
        False
    ):

        print()
        print("=" * 70)

        print(
            "RESULT: FILE NOT YET RECOGNIZED"
        )

        print("=" * 70)

        print()
        print(
            "This is NOT a syntax error."
        )

        print(
            "The current Universal Reader could "
            "not confidently understand this "
            "holdings format."
        )

        print()
        print(
            "Next action: inspect the workbook "
            "structure and expand the universal "
            "content-detection rules."
        )

        return

    # -----------------------------------------------------
    # STEP 3 - Extract holdings only after safe detection
    # -----------------------------------------------------

    print()
    print("Extracting holdings...")

    try:

        detection, holdings = reader.read(
            FILE_PATH
        )

    except Exception as error:

        print()
        print("=" * 70)
        print("EXTRACTION ERROR")
        print("=" * 70)

        print(
            type(error).__name__
        )

        print(
            str(error)
        )

        return

    # -----------------------------------------------------
    # STEP 4 - Display universal holdings
    # -----------------------------------------------------

    print()
    print(
        "Holdings Extracted:",
        len(holdings)
    )

    for holding in holdings:

        print()
        print("-" * 70)

        print(
            f"Broker:          "
            f"{holding.broker}"
        )

        print(
            f"Asset Type:      "
            f"{holding.asset_type}"
        )

        print(
            f"Symbol:          "
            f"{holding.symbol}"
        )

        print(
            f"Name:            "
            f"{holding.name}"
        )

        print(
            f"ISIN:            "
            f"{holding.isin}"
        )

        print(
            f"Quantity:        "
            f"{holding.quantity:,.4f}"
        )

        print(
            f"Average Price:   "
            f"₹{holding.average_price:,.2f}"
        )

        print(
            f"Current Price:   "
            f"₹{holding.current_price:,.2f}"
        )

        print(
            f"Invested Value:  "
            f"₹{holding.invested_value:,.2f}"
        )

        print(
            f"Current Value:   "
            f"₹{holding.current_value:,.2f}"
        )

        print(
            f"Profit / Loss:   "
            f"₹{holding.profit_loss:,.2f}"
        )

        print(
            f"P/L %:           "
            f"{holding.profit_loss_percent:.2f}%"
        )

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()