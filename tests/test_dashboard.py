from streamlit.testing.v1 import AppTest


def test_dashboard_loads():

    app = AppTest.from_file(
        "ui/dashboard.py"
    )

    app.run(
        timeout=10
    )

    assert not app.exception

    print(
        "Dashboard UI render smoke test: PASS"
    )


if __name__ == "__main__":

    test_dashboard_loads()

    print(
        "SPRINT 0.8.1 DASHBOARD UI TEST: PASS"
    )
