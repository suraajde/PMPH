from streamlit.testing.v1 import AppTest


def test_portfolio_view_loads():

    app = AppTest.from_file(
        "ui/portfolio_view.py"
    )

    app.run(
        timeout=10
    )

    assert not app.exception

    print(
        "Portfolio UI render smoke test: PASS"
    )


if __name__ == "__main__":

    test_portfolio_view_loads()

    print(
        "SPRINT 0.7.2 PORTFOLIO UI TEST: PASS"
    )
