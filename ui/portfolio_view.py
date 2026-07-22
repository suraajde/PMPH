import streamlit as st

from services.portfolio_read_service import (
    PortfolioReadService,
)


DATABASE_PATH = "data/pmph_portfolio.db"


def get_holdings_column_config():
    """
    Shared display formatting for portfolio holdings tables.

    Formatting affects presentation only.
    Underlying portfolio values remain numeric.
    """

    return {
        "Quantity": st.column_config.NumberColumn(
            "Quantity",
            format="%.2f",
        ),
        "Average Price": st.column_config.NumberColumn(
            "Average Price",
            format="₹ %.2f",
        ),
        "Current Price": st.column_config.NumberColumn(
            "Current Price",
            format="₹ %.2f",
        ),
        "Invested Value": st.column_config.NumberColumn(
            "Invested Value",
            format="₹ %.2f",
        ),
        "Current Value": st.column_config.NumberColumn(
            "Current Value",
            format="₹ %.2f",
        ),
        "Profit / Loss": st.column_config.NumberColumn(
            "Profit / Loss",
            format="₹ %.2f",
        ),
        "Return %": st.column_config.NumberColumn(
            "Return %",
            format="%.2f %%",
        ),
        "Accounts": st.column_config.NumberColumn(
            "Accounts",
            format="%d",
        ),
    }


def show():

    st.title("Portfolio")

    service = PortfolioReadService(
        database_path=DATABASE_PATH,
    )

    summary = (
        service.get_portfolio_summary()
    )

    if summary["holding_count"] == 0:

        st.info(
            "No persisted portfolio holdings found."
        )

        return

    # =====================================================
    # PORTFOLIO SUMMARY
    # =====================================================

    st.subheader(
        "Portfolio Summary"
    )

    column_1, column_2, column_3, column_4 = (
        st.columns(4)
    )

    column_1.metric(
        "Accounts",
        summary["account_count"],
    )

    column_2.metric(
        "Holdings",
        summary["holding_count"],
    )

    column_3.metric(
        "Invested Value",
        f"₹{summary['invested_value']:,.2f}",
    )

    column_4.metric(
        "Current Value",
        f"₹{summary['current_value']:,.2f}",
    )

    column_5, column_6 = st.columns(2)

    column_5.metric(
        "Profit / Loss",
        f"₹{summary['profit_loss']:,.2f}",
    )

    column_6.metric(
        "Return",
        f"{summary['profit_loss_percent']:.2f}%",
    )

    # =====================================================
    # CONSOLIDATED PORTFOLIO
    # =====================================================

    st.markdown("---")

    st.subheader(
        "Consolidated Holdings"
    )

    consolidated_holdings = (
        service.get_consolidated_holdings()
    )

    consolidated_rows = []

    for holding in consolidated_holdings:

        consolidated_rows.append(
            {
                "Symbol": holding["symbol"],
                "Name": holding["name"],
                "Asset Type": holding[
                    "asset_type"
                ],
                "Quantity": holding[
                    "quantity"
                ],
                "Average Price": holding[
                    "average_price"
                ],
                "Current Price": holding[
                    "current_price"
                ],
                "Invested Value": holding[
                    "invested_value"
                ],
                "Current Value": holding[
                    "current_value"
                ],
                "Profit / Loss": holding[
                    "profit_loss"
                ],
                "Return %": holding[
                    "profit_loss_percent"
                ],
                "Accounts": holding[
                    "account_count"
                ],
            }
        )

    st.dataframe(
        consolidated_rows,
        use_container_width=True,
        hide_index=True,
        column_config=get_holdings_column_config(),
    )

    # =====================================================
    # ACCOUNT-WISE PORTFOLIO
    # =====================================================

    st.markdown("---")

    st.subheader(
        "Account-wise Holdings"
    )

    account_portfolios = (
        service.get_all_account_portfolios(
            active_only=True
        )
    )

    for portfolio in account_portfolios:

        account = portfolio["account"]

        with st.expander(
            (
                f"{account.display_name()} "
                f"({portfolio['holding_count']} holdings)"
            ),
            expanded=False,
        ):

            account_rows = []

            for holding in portfolio[
                "holdings"
            ]:

                account_rows.append(
                    {
                        "Symbol": holding.symbol,
                        "Name": holding.name,
                        "Asset Type": (
                            holding.asset_type
                        ),
                        "Quantity": (
                            holding.quantity
                        ),
                        "Average Price": (
                            holding.average_price
                        ),
                        "Current Price": (
                            holding.current_price
                        ),
                        "Invested Value": (
                            holding.invested_value
                        ),
                        "Current Value": (
                            holding.current_value
                        ),
                        "Profit / Loss": (
                            holding.profit_loss
                        ),
                        "Return %": (
                            holding.profit_loss_percent
                        ),
                    }
                )

            st.dataframe(
                account_rows,
                use_container_width=True,
                hide_index=True,
                column_config=get_holdings_column_config(),
            )
