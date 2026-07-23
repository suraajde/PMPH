import altair as alt
import pandas as pd
import streamlit as st

from services.portfolio_read_service import PortfolioReadService
from services.portfolio_status_service import PortfolioStatusService
from services.portfolio_analytics_service import PortfolioAnalyticsService
from services.portfolio_health_service import PortfolioHealthService


DATABASE_PATH = "data/pmph_portfolio.db"


def show():

    st.title("Dashboard")

    read_service = PortfolioReadService(
        database_path=DATABASE_PATH,
    )

    status_service = PortfolioStatusService(
        database_path=DATABASE_PATH,
    )

    portfolio_status = (
        status_service
        .get_portfolio_status()
    )

    summary = (
        read_service
        .get_portfolio_summary()
    )

    consolidated_holdings = (
        read_service
        .get_consolidated_holdings()
    )

    account_portfolios = (
        read_service
        .get_all_account_portfolios()
    )

    if not consolidated_holdings:

        st.info(
            "No persisted portfolio holdings are available."
        )

        return

    # =====================================================
    # PORTFOLIO OVERVIEW
    # =====================================================

    st.subheader(
        "Portfolio Overview"
    )

    metric_columns = st.columns(
        4
    )

    metric_columns[0].metric(
        "Current Value",
        f"₹{summary['current_value']:,.2f}",
    )

    metric_columns[1].metric(
        "Invested Value",
        f"₹{summary['invested_value']:,.2f}",
    )

    metric_columns[2].metric(
        "Profit / Loss",
        f"₹{summary['profit_loss']:,.2f}",
    )

    metric_columns[3].metric(
        "Portfolio Return",
        (
            f"{summary['profit_loss_percent']:.2f}%"
        ),
    )

    secondary_columns = st.columns(
        3
    )

    secondary_columns[0].metric(
        "Accounts",
        summary["account_count"],
    )

    secondary_columns[1].metric(
        "Holdings",
        summary["holding_count"],
    )

    secondary_columns[2].metric(
        "Consolidated Securities",
        summary["consolidated_holding_count"],
    )

    # =====================================================
    # DATA AND VALUATION STATUS
    # =====================================================

    st.markdown("---")

    st.subheader(
        "Data & Valuation Status"
    )

    status_columns = st.columns(
        4
    )

    status_columns[0].metric(
        "Valuation Coverage",
        (
            f"{portfolio_status['valuation_coverage_percent']:.2f}%"
        ),
    )

    status_columns[1].metric(
        "Valued Holdings",
        (
            f"{portfolio_status['valuation_covered_count']} / "
            f"{portfolio_status['holding_count']}"
        ),
    )

    status_columns[2].metric(
        "Source Files",
        portfolio_status["source_file_count"],
    )

    status_columns[3].metric(
        "Market Freshness",
        "Not Tracked"
    )

    latest_record_update = portfolio_status[
        "latest_record_update"
    ]

    if latest_record_update:

        st.caption(
            "Latest persisted record update: "
            + latest_record_update.strftime(
                "%d %b %Y, %I:%M %p"
            )
        )

    if portfolio_status["market_valuation_freshness"] == "NOT_TRACKED":

        st.info(
            "Market valuation freshness is not yet tracked. "
            "The timestamp above represents the latest persisted "
            "record update and must not be interpreted as a live "
            "market-price timestamp."
        )

    # =====================================================
    # SECURITY COMPOSITION
    # =====================================================

    st.markdown("---")

    st.subheader(
        "Portfolio Composition"
    )

    total_current_value = (
        summary["current_value"]
    )

    composition_rows = []

    for holding in consolidated_holdings:

        current_value = (
            holding["current_value"]
        )

        allocation_percent = (
            (
                current_value
                / total_current_value
            )
            * 100
            if total_current_value
            else 0
        )

        composition_rows.append(
            {
                "Security": (
                    holding["symbol"]
                ),
                "Asset Type": (
                    holding["asset_type"]
                ),
                "Current Value": (
                    current_value
                ),
                "Allocation %": (
                    allocation_percent
                ),
                "Return %": (
                    holding[
                        "profit_loss_percent"
                    ]
                ),
            }
        )

    composition_rows.sort(
        key=lambda row: row[
            "Current Value"
        ],
        reverse=True,
    )

    composition_frame = pd.DataFrame(
        composition_rows
    )

    allocation_chart = (
        alt.Chart(
            composition_frame
        )
        .mark_bar()
        .encode(
            x=alt.X(
                "Allocation %:Q",
                title="Portfolio Allocation (%)",
            ),
            y=alt.Y(
                "Security:N",
                sort="-x",
                title=None,
            ),
            tooltip=[
                alt.Tooltip(
                    "Security:N",
                    title="Security",
                ),
                alt.Tooltip(
                    "Current Value:Q",
                    title="Current Value",
                    format=",.2f",
                ),
                alt.Tooltip(
                    "Allocation %:Q",
                    title="Allocation",
                    format=".2f",
                ),
                alt.Tooltip(
                    "Return %:Q",
                    title="Return",
                    format=".2f",
                ),
            ],
        )
        .properties(
            height=220,
        )
    )

    st.altair_chart(
        allocation_chart,
        use_container_width=True,
    )

    st.dataframe(
        composition_rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Current Value": (
                st.column_config.NumberColumn(
                    "Current Value",
                    format="₹ %.2f",
                )
            ),
            "Allocation %": (
                st.column_config.NumberColumn(
                    "Allocation %",
                    format="%.2f %%",
                )
            ),
            "Return %": (
                st.column_config.NumberColumn(
                    "Return %",
                    format="%.2f %%",
                )
            ),
        },
    )

    # =====================================================
    # ACCOUNT ALLOCATION
    # =====================================================

    st.markdown("---")

    st.subheader(
        "Account Allocation"
    )

    account_rows = []

    for portfolio in account_portfolios:

        account = portfolio[
            "account"
        ]

        holdings = portfolio[
            "holdings"
        ]

        account_current_value = sum(
            holding.current_value
            for holding in holdings
        )

        allocation_percent = (
            (
                account_current_value
                / total_current_value
            )
            * 100
            if total_current_value
            else 0
        )

        account_rows.append(
            {
                "Owner": (
                    account.owner_name
                ),
                "Platform": (
                    account.platform_name
                ),
                "Account": (
                    account.account_name
                ),
                "Holdings": (
                    portfolio[
                        "holding_count"
                    ]
                ),
                "Current Value": (
                    account_current_value
                ),
                "Allocation %": (
                    allocation_percent
                ),
            }
        )

    account_rows.sort(
        key=lambda row: row[
            "Current Value"
        ],
        reverse=True,
    )

    st.dataframe(
        account_rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Current Value": (
                st.column_config.NumberColumn(
                    "Current Value",
                    format="₹ %.2f",
                )
            ),
            "Allocation %": (
                st.column_config.NumberColumn(
                    "Allocation %",
                    format="%.2f %%",
                )
            ),
        },
    )

    # =====================================================
    # ASSET TYPE STATUS
    # =====================================================

    st.markdown("---")

    st.subheader(
        "Asset Type Summary"
    )

    asset_totals = {}

    for holding in consolidated_holdings:

        asset_type = (
            holding["asset_type"]
            or "Unknown"
        )

        asset_totals[
            asset_type
        ] = (
            asset_totals.get(
                asset_type,
                0,
            )
            + holding[
                "current_value"
            ]
        )

    asset_rows = []

    for (
        asset_type,
        current_value,
    ) in asset_totals.items():

        allocation_percent = (
            (
                current_value
                / total_current_value
            )
            * 100
            if total_current_value
            else 0
        )

        asset_rows.append(
            {
                "Asset Type": asset_type,
                "Current Value": (
                    current_value
                ),
                "Allocation %": (
                    allocation_percent
                ),
            }
        )

    st.dataframe(
        asset_rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Current Value": (
                st.column_config.NumberColumn(
                    "Current Value",
                    format="₹ %.2f",
                )
            ),
            "Allocation %": (
                st.column_config.NumberColumn(
                    "Allocation %",
                    format="%.2f %%",
                )
            ),
        },
    )
    # =====================================================
    # PORTFOLIO HEALTH - CONCENTRATION ANALYTICS
    # =====================================================

    st.markdown("---")

    st.subheader(
        "Portfolio Health - Concentration Analytics"
    )

    st.caption(
        "Position-level analytics for holdings currently "
        "imported and persisted in PMPH."
    )

    analytics_service = PortfolioAnalyticsService(
        database_path=DATABASE_PATH,
    )

    concentration_summary = (
        analytics_service
        .get_concentration_summary()
    )

    allocation_diagnostics = (
        analytics_service
        .get_allocation_diagnostics()
    )

    security_concentration = (
        analytics_service
        .get_security_concentration()
    )

    account_concentration = (
        analytics_service
        .get_account_concentration()
    )

    if (
        allocation_diagnostics[
            "portfolio_completeness"
        ]
        != "CONFIRMED"
    ):

        st.warning(
            "Analysis Scope: These diagnostics are based only on "
            "holdings currently imported into PMPH. Portfolio "
            "completeness has not been confirmed. Percentages shown "
            "below represent allocation within the imported holdings "
            "only and must not be interpreted as allocation across "
            "the complete investment portfolio."
        )

    concentration_columns = st.columns(
        4
    )

    concentration_columns[0].metric(
        "Largest Position",
        (
            f"{concentration_summary['largest_position_percent']:.2f}%"
        ),
    )

    concentration_columns[1].metric(
        "Top 3 Concentration",
        (
            f"{concentration_summary['top_3_percent']:.2f}%"
        ),
    )

    concentration_columns[2].metric(
        "Effective Positions",
        (
            f"{concentration_summary['effective_security_positions']:.2f}"
        ),
    )

    concentration_columns[3].metric(
        "Largest Account",
        (
            f"{concentration_summary['largest_account_percent']:.2f}%"
        ),
    )

    st.markdown(
        "**Security Concentration**"
    )

    security_rows = []

    for position in security_concentration[
        "positions"
    ]:

        security_rows.append(
            {
                "Security": position["symbol"],
                "Current Value": (
                    position["current_value"]
                ),
                "Imported Holdings Weight %": (
                    position["weight_percent"]
                ),
            }
        )

    st.dataframe(
        security_rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Current Value": (
                st.column_config.NumberColumn(
                    "Current Value",
                    format="₹ %.2f",
                )
            ),
            "Imported Holdings Weight %": (
                st.column_config.NumberColumn(
                    "Imported Holdings Weight %",
                    format="%.2f %%",
                )
            ),
        },
    )

    st.markdown(
        "**Account Concentration**"
    )

    concentration_account_rows = []

    for account_item in account_concentration[
        "accounts"
    ]:

        concentration_account_rows.append(
            {
                "Owner": (
                    account_item["owner_name"]
                ),
                "Platform": (
                    account_item["platform_name"]
                ),
                "Account": (
                    account_item["account_name"]
                ),
                "Current Value": (
                    account_item["current_value"]
                ),
                "Imported Holdings Weight %": (
                    account_item["weight_percent"]
                ),
            }
        )

    st.dataframe(
        concentration_account_rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Current Value": (
                st.column_config.NumberColumn(
                    "Current Value",
                    format="₹ %.2f",
                )
            ),
            "Imported Holdings Weight %": (
                st.column_config.NumberColumn(
                    "Imported Holdings Weight %",
                    format="%.2f %%",
                )
            ),
        },
    )

    st.info(
        "Current analytics measure concentration only within the "
        "holdings imported into PMPH. They do not establish the "
        "allocation or concentration of the complete investment "
        "portfolio. Underlying diversification inside ETFs or mutual "
        "funds is not yet measured, and fund/ETF overlap analysis is "
        "not yet available."
    )
    # =====================================================
    # PORTFOLIO HEALTH - DIAGNOSTIC FRAMEWORK
    # =====================================================

    st.markdown("---")

    st.subheader(
        "Portfolio Health - Diagnostic Framework"
    )

    st.caption(
        "Structured factual observations derived from holdings "
        "currently imported and persisted in PMPH."
    )

    health_service = PortfolioHealthService(
        database_path=DATABASE_PATH,
    )

    health_diagnostics = (
        health_service
        .get_health_diagnostics()
    )

    health_columns = st.columns(
        4
    )

    health_columns[0].metric(
        "Framework Status",
        "Observation Only",
    )

    health_columns[1].metric(
        "Analysis Scope",
        "Imported Holdings Only",
    )

    health_columns[2].metric(
        "Portfolio Completeness",
        (
            "Not Confirmed"
            if health_diagnostics[
                "portfolio_completeness"
            ] != "CONFIRMED"
            else "Confirmed"
        ),
    )

    health_columns[3].metric(
        "Health Score",
        "Not Available",
    )

    st.warning(
        "Portfolio Health Scope: The current diagnostic framework "
        "uses only holdings imported into PMPH. These holdings do "
        "not currently represent a confirmed complete investment "
        "portfolio. Observations below must therefore be interpreted "
        "only within the imported holdings and not as complete-portfolio "
        "health conclusions."
    )

    st.markdown(
        "**Current Diagnostic Observations**"
    )

    observation_rows = []

    for observation in health_diagnostics[
        "observations"
    ]:

        observation_rows.append(
            {
                "Dimension": (
                    observation[
                        "dimension"
                    ]
                ),
                "Observation": (
                    observation[
                        "message"
                    ]
                ),
                "Source": (
                    observation[
                        "source"
                    ]
                ),
            }
        )

    if observation_rows:

        st.dataframe(
            observation_rows,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No portfolio-health diagnostic observations are "
            "currently available for the imported holdings."
        )

    st.info(
        "Framework Boundary: PMPH currently provides factual "
        "diagnostic observations only. Portfolio health scoring, "
        "target allocation, investment recommendations, underlying "
        "ETF/fund diversification, fund overlap, and market-dependent "
        "risk or performance analytics are not yet available."
    )
