from services.importer import UniversalImporter


FILE_PATH = r"D:\PMPH\data\Holdings_prostocks.xlsx"


def main():

    print("=" * 70)
    print("PMPH UNIVERSAL IMPORT ENGINE")
    print("=" * 70)

    importer = UniversalImporter()

    broker = importer.detect_broker(
        FILE_PATH
    )

    print()
    print("Detected Broker:")
    print(broker)

    parser = importer.get_parser(
        broker
    )

    if parser is None:

        print()
        print("No parser available.")

        return

    holdings = parser.parse(
        FILE_PATH
    )

    print()
    print(
        f"Holdings Extracted: {len(holdings)}"
    )

    print()

    for holding in holdings:

        print("-" * 70)

        print(
            f"Broker:          {holding.broker}"
        )

        print(
            f"Asset Type:      {holding.asset_type}"
        )

        print(
            f"Symbol:          {holding.symbol}"
        )

        print(
            f"Quantity:        {holding.quantity:,.4f}"
        )

        print(
            f"Average Price:   ₹{holding.average_price:,.2f}"
        )

        print(
            f"Current Price:   ₹{holding.current_price:,.2f}"
        )

        print(
            f"Invested Value:  ₹{holding.invested_value:,.2f}"
        )

        print(
            f"Current Value:   ₹{holding.current_value:,.2f}"
        )

        print(
            f"Profit / Loss:   ₹{holding.profit_loss:,.2f}"
        )

        print(
            f"P/L %:           {holding.profit_loss_percent:.2f}%"
        )

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()