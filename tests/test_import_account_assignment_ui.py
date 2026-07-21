import streamlit as st

from services.portfolio_import_service import (
    PortfolioImportService,
)

from ui.import_account_assignment import (
    show_account_assignment,
)


def main():

    st.title(
        "PMPH Account Assignment UI Test"
    )

    st.info(
        "This is an isolated test of the "
        "file-to-account assignment component."
    )

    service = (
        PortfolioImportService(
            "data/test_account_assignment_ui.db"
        )
    )

    result = (
        show_account_assignment(
            file_name=(
                "sample_holdings.xlsx"
            ),
            import_service=service,
        )
    )

    st.markdown("---")

    st.subheader(
        "Assignment Result"
    )

    if result["ready"]:

        st.success(
            "Assignment Ready"
        )

        st.write(
            "Account:",
            result[
                "account"
            ].display_name()
        )

        st.write(
            "Import Mode:",
            result[
                "mode"
            ]
        )

    else:

        st.warning(
            "Create or select an account "
            "to complete the assignment."
        )


if __name__ == "__main__":

    main()