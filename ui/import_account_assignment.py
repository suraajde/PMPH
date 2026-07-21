import streamlit as st

from services.portfolio_import_service import (
    PortfolioImportService,
)


def initialize_assignment_state():

    if "holdings_file_assignments" not in st.session_state:
        st.session_state.holdings_file_assignments = {}


def _assignment_key(file_name):

    return str(file_name).strip()


def show_account_assignment(
    file_name,
    import_service: PortfolioImportService,
):

    """
    Display account assignment controls for one uploaded file.

    Returns a dictionary containing:

    {
        "ready": bool,
        "account": PortfolioAccount | None,
        "mode": "FULL" | "PARTIAL",
    }
    """

    initialize_assignment_state()

    key = _assignment_key(
        file_name
    )

    st.markdown(
        f"#### 📄 {file_name}"
    )

    existing_accounts = (
        import_service.get_accounts(
            active_only=True
        )
    )

    account_options = [
        "➕ Create New Account"
    ]

    account_lookup = {}

    for account in existing_accounts:

        display_name = (
            account.display_name()
        )

        account_options.append(
            display_name
        )

        account_lookup[
            display_name
        ] = account

    selected_option = st.selectbox(
        "Portfolio Account",
        options=account_options,
        key=f"account_select_{key}",
        help=(
            "Choose the owner/broker/account that "
            "this holdings file belongs to."
        ),
    )

    selected_account = None

    # =====================================================
    # EXISTING ACCOUNT
    # =====================================================

    if (
        selected_option
        != "➕ Create New Account"
    ):

        selected_account = (
            account_lookup[
                selected_option
            ]
        )

        st.success(
            "Assigned to: "
            f"{selected_account.display_name()}"
        )

    # =====================================================
    # CREATE NEW ACCOUNT
    # =====================================================

    else:

        st.caption(
            "Create the portfolio account that owns "
            "the holdings in this file."
        )

        owner_col, platform_col = (
            st.columns(2)
        )

        with owner_col:

            owner_name = st.text_input(
                "Owner Name",
                key=f"owner_{key}",
                placeholder="Example: Suraj",
            )

        with platform_col:

            platform_name = st.text_input(
                "Platform / Broker",
                key=f"platform_{key}",
                placeholder=(
                    "Example: Groww, Zerodha, ProStocks"
                ),
            )

        account_name = st.text_input(
            "Account Name",
            key=f"account_name_{key}",
            placeholder="Example: Main Portfolio",
        )

        create_clicked = st.button(
            "Create & Assign Account",
            key=f"create_account_{key}",
            use_container_width=True,
        )

        if create_clicked:

            if not owner_name.strip():

                st.error(
                    "Owner Name is required."
                )

            elif not platform_name.strip():

                st.error(
                    "Platform / Broker is required."
                )

            elif not account_name.strip():

                st.error(
                    "Account Name is required."
                )

            else:

                try:

                    selected_account = (
                        import_service
                        .get_or_create_account(
                            owner_name=(
                                owner_name.strip()
                            ),
                            platform_name=(
                                platform_name.strip()
                            ),
                            account_name=(
                                account_name.strip()
                            ),
                        )
                    )

                    st.session_state[
                        "holdings_file_assignments"
                    ][key] = {
                        "account_id":
                            selected_account.account_id
                    }

                    st.success(
                        "Account created and assigned: "
                        f"{selected_account.display_name()}"
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        "Unable to create account: "
                        f"{error}"
                    )

        # ---------------------------------------------
        # Recover account created on previous rerun
        # ---------------------------------------------

        saved_assignment = (
            st.session_state[
                "holdings_file_assignments"
            ].get(
                key
            )
        )

        if saved_assignment:

            account_id = (
                saved_assignment.get(
                    "account_id"
                )
            )

            for account in (
                existing_accounts
            ):

                if (
                    account.account_id
                    == account_id
                ):

                    selected_account = (
                        account
                    )

                    st.info(
                        "Previously assigned to: "
                        f"{account.display_name()}"
                    )

                    break

    # =====================================================
    # IMPORT MODE
    # =====================================================

    st.markdown(
        "**Import Type**"
    )

    import_mode_label = (
        st.radio(
            "How should PMPH treat this file?",
            options=[
                "FULL Statement",
                "PARTIAL Update",
            ],
            key=f"import_mode_{key}",
            horizontal=True,
            label_visibility="collapsed",
        )
    )

    if (
        import_mode_label
        == "FULL Statement"
    ):

        import_mode = "FULL"

        st.warning(
            "FULL Statement means this file represents "
            "the complete current holdings for this account. "
            "Existing securities that are absent from this "
            "statement may be removed from the current "
            "portfolio."
        )

    else:

        import_mode = "PARTIAL"

        st.info(
            "PARTIAL Update adds or updates the securities "
            "present in this file. Existing holdings that "
            "are absent from this file will not be removed."
        )

    # =====================================================
    # SAVE CURRENT ASSIGNMENT
    # =====================================================

    if selected_account is not None:

        st.session_state[
            "holdings_file_assignments"
        ][key] = {
            "account_id":
                selected_account.account_id,

            "mode":
                import_mode,
        }

    ready = (
        selected_account
        is not None
    )

    return {
        "ready":
            ready,

        "account":
            selected_account,

        "mode":
            import_mode,
    }


def clear_file_assignment(
    file_name,
):

    initialize_assignment_state()

    key = _assignment_key(
        file_name
    )

    st.session_state[
        "holdings_file_assignments"
    ].pop(
        key,
        None,
    )


def clear_all_assignments():

    st.session_state[
        "holdings_file_assignments"
    ] = {}