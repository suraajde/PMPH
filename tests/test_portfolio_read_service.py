from pathlib import Path

from models.account import PortfolioAccount
from models.stored_holding import StoredHolding

from services.portfolio_database import PortfolioDatabase
from services.holdings_database import HoldingsDatabase
from services.portfolio_read_service import PortfolioReadService


def reset_database(
    database_path,
):

    if database_path.exists():
        database_path.unlink()


def test_account_portfolio_read():

    database_path = Path(
        r"D:\PMPH\data\test_portfolio_read_account.db"
    )

    reset_database(
        database_path
    )

    portfolio_database = PortfolioDatabase(
        str(database_path)
    )

    holdings_database = HoldingsDatabase(
        str(database_path)
    )

    account = PortfolioAccount(
        owner_name="Test Owner",
        platform_name="Test Broker",
        account_name="Primary",
    )

    portfolio_database.save_account(
        account
    )

    holding = StoredHolding(
        account_id=account.account_id,
        symbol="TESTETF",
        name="Test ETF",
        isin="INE000TEST01",
        asset_type="ETF",
        quantity=10.0,
        average_price=100.0,
        current_price=120.0,
        invested_value=1000.0,
        current_value=1200.0,
        profit_loss=200.0,
        profit_loss_percent=20.0,
    )

    holdings_database.save_holding(
        holding
    )

    read_service = PortfolioReadService(
        str(database_path)
    )

    result = (
        read_service.get_account_portfolio(
            account.account_id
        )
    )

    assert result is not None

    assert (
        result["account"].account_id
        == account.account_id
    )

    assert result["holding_count"] == 1

    assert len(
        result["holdings"]
    ) == 1

    assert (
        result["holdings"][0].symbol
        == "TESTETF"
    )

    print(
        "Account-wise portfolio read: PASS"
    )





def test_all_account_portfolios_read():

    database_path = Path(
        r"D:\PMPH\data\test_portfolio_read_all_accounts.db"
    )

    reset_database(
        database_path
    )

    portfolio_database = PortfolioDatabase(
        str(database_path)
    )

    holdings_database = HoldingsDatabase(
        str(database_path)
    )

    account_one = PortfolioAccount(
        owner_name="Owner One",
        platform_name="Broker One",
        account_name="Primary",
    )

    account_two = PortfolioAccount(
        owner_name="Owner Two",
        platform_name="Broker Two",
        account_name="Primary",
    )

    portfolio_database.save_account(
        account_one
    )

    portfolio_database.save_account(
        account_two
    )

    holding_one = StoredHolding(
        account_id=account_one.account_id,
        symbol="ETFONE",
        name="ETF One",
        isin="INE000TEST01",
        asset_type="ETF",
        quantity=10.0,
        average_price=100.0,
        current_price=110.0,
        invested_value=1000.0,
        current_value=1100.0,
        profit_loss=100.0,
        profit_loss_percent=10.0,
    )

    holding_two = StoredHolding(
        account_id=account_two.account_id,
        symbol="ETFTWO",
        name="ETF Two",
        isin="INE000TEST02",
        asset_type="ETF",
        quantity=20.0,
        average_price=200.0,
        current_price=220.0,
        invested_value=4000.0,
        current_value=4400.0,
        profit_loss=400.0,
        profit_loss_percent=10.0,
    )

    holdings_database.save_holding(
        holding_one
    )

    holdings_database.save_holding(
        holding_two
    )

    read_service = PortfolioReadService(
        str(database_path)
    )

    portfolios = (
        read_service
        .get_all_account_portfolios()
    )

    assert len(portfolios) == 2

    portfolio_by_account_id = {
        portfolio["account"].account_id:
        portfolio
        for portfolio in portfolios
    }

    first = portfolio_by_account_id[
        account_one.account_id
    ]

    second = portfolio_by_account_id[
        account_two.account_id
    ]

    assert first["holding_count"] == 1
    assert second["holding_count"] == 1

    assert (
        first["holdings"][0].symbol
        == "ETFONE"
    )

    assert (
        second["holdings"][0].symbol
        == "ETFTWO"
    )

    print(
        "All-account grouped portfolio read: PASS"
    )


def test_consolidated_holdings_read():

    database_path = Path(
        r"D:\PMPH\data\test_portfolio_read_consolidated.db"
    )

    reset_database(
        database_path
    )

    portfolio_database = PortfolioDatabase(
        str(database_path)
    )

    holdings_database = HoldingsDatabase(
        str(database_path)
    )

    account_one = PortfolioAccount(
        owner_name="Owner One",
        platform_name="Broker One",
        account_name="Primary",
    )

    account_two = PortfolioAccount(
        owner_name="Owner Two",
        platform_name="Broker Two",
        account_name="Primary",
    )

    portfolio_database.save_account(
        account_one
    )

    portfolio_database.save_account(
        account_two
    )

    holding_one = StoredHolding(
        account_id=account_one.account_id,
        symbol="SAMEETF",
        name="Same ETF",
        isin="INE000SAME01",
        asset_type="ETF",
        quantity=10.0,
        average_price=100.0,
        current_price=120.0,
        invested_value=1000.0,
        current_value=1200.0,
        profit_loss=200.0,
        profit_loss_percent=20.0,
    )

    holding_two = StoredHolding(
        account_id=account_two.account_id,
        symbol="SAMEETF",
        name="Same ETF",
        isin="INE000SAME01",
        asset_type="ETF",
        quantity=20.0,
        average_price=110.0,
        current_price=120.0,
        invested_value=2200.0,
        current_value=2400.0,
        profit_loss=200.0,
        profit_loss_percent=9.090909,
    )

    holdings_database.save_holding(
        holding_one
    )

    holdings_database.save_holding(
        holding_two
    )

    read_service = PortfolioReadService(
        str(database_path)
    )

    consolidated = (
        read_service
        .get_consolidated_holdings()
    )

    assert len(consolidated) == 1

    item = consolidated[0]

    assert item["quantity"] == 30.0
    assert item["invested_value"] == 3200.0
    assert item["current_value"] == 3600.0
    assert item["profit_loss"] == 400.0

    assert round(
        item["average_price"],
        2,
    ) == 106.67

    assert round(
        item["current_price"],
        2,
    ) == 120.00

    assert round(
        item["profit_loss_percent"],
        2,
    ) == 12.50

    assert item["account_count"] == 2

    assert len(
        item["account_ids"]
    ) == 2

    assert (
        holdings_database.count_holdings()
        == 2
    )

    print(
        "Consolidated holdings read: PASS"
    )




def test_portfolio_summary():

    database_path = Path(
        r"D:\PMPH\data\test_portfolio_read_summary.db"
    )

    reset_database(
        database_path
    )

    portfolio_database = PortfolioDatabase(
        str(database_path)
    )

    holdings_database = HoldingsDatabase(
        str(database_path)
    )

    account_one = PortfolioAccount(
        owner_name="Owner One",
        platform_name="Broker One",
        account_name="Primary",
    )

    account_two = PortfolioAccount(
        owner_name="Owner Two",
        platform_name="Broker Two",
        account_name="Primary",
    )

    portfolio_database.save_account(
        account_one
    )

    portfolio_database.save_account(
        account_two
    )

    holdings = [
        StoredHolding(
            account_id=account_one.account_id,
            symbol="SAMEETF",
            name="Same ETF",
            isin="INE000SAME01",
            asset_type="ETF",
            quantity=10.0,
            average_price=100.0,
            current_price=120.0,
            invested_value=1000.0,
            current_value=1200.0,
            profit_loss=200.0,
            profit_loss_percent=20.0,
        ),
        StoredHolding(
            account_id=account_two.account_id,
            symbol="SAMEETF",
            name="Same ETF",
            isin="INE000SAME01",
            asset_type="ETF",
            quantity=20.0,
            average_price=110.0,
            current_price=120.0,
            invested_value=2200.0,
            current_value=2400.0,
            profit_loss=200.0,
            profit_loss_percent=9.090909,
        ),
        StoredHolding(
            account_id=account_two.account_id,
            symbol="OTHERETF",
            name="Other ETF",
            isin="INE000OTHER1",
            asset_type="ETF",
            quantity=5.0,
            average_price=200.0,
            current_price=220.0,
            invested_value=1000.0,
            current_value=1100.0,
            profit_loss=100.0,
            profit_loss_percent=10.0,
        ),
    ]

    for holding in holdings:

        holdings_database.save_holding(
            holding
        )

    read_service = PortfolioReadService(
        str(database_path)
    )

    summary = (
        read_service.get_portfolio_summary()
    )

    assert summary["account_count"] == 2
    assert summary["holding_count"] == 3

    assert (
        summary["consolidated_holding_count"]
        == 2
    )

    assert summary["invested_value"] == 4200.0
    assert summary["current_value"] == 4700.0
    assert summary["profit_loss"] == 500.0

    assert round(
        summary["profit_loss_percent"],
        2,
    ) == 11.90

    print(
        "Portfolio summary read: PASS"
    )
