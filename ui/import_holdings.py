import os
import tempfile

import pandas as pd
import streamlit as st

from services.holdings_validator import HoldingsValidator
from services.universal_holdings_reader import UniversalHoldingsReader
from services.portfolio_import_service import PortfolioImportService
from services.portfolio_batch_import_service import PortfolioBatchImportService, BatchImportItem

from ui.import_account_assignment import (
    show_account_assignment,
)


# =========================================================
# SESSION STATE
# =========================================================

def initialize_import_state():

    if "holdings_file_basket" not in st.session_state:
        st.session_state.holdings_file_basket = {}

    if "holdings_analysis_requested" not in st.session_state:
        st.session_state.holdings_analysis_requested = False


# =========================================================
# FILE BASKET
# =========================================================

def add_file_to_basket(uploaded_file):

    if uploaded_file is None:
        return

    file_bytes = uploaded_file.getvalue()

    file_key = (
        uploaded_file.name,
        len(file_bytes),
    )

    st.session_state.holdings_file_basket[
        file_key
    ] = {
        "name": uploaded_file.name,
        "bytes": file_bytes,
        "size": len(file_bytes),
    }

    st.session_state.holdings_analysis_requested = False


def remove_file_from_basket(file_key):

    if (
        file_key
        in st.session_state.holdings_file_basket
    ):

        del st.session_state.holdings_file_basket[
            file_key
        ]

    st.session_state.holdings_analysis_requested = False


def clear_file_basket():

    st.session_state.holdings_file_basket = {}

    st.session_state.holdings_analysis_requested = False


# =========================================================
# MAIN SCREEN
# =========================================================

def show():

    initialize_import_state()

    # =====================================================
    # HEADER
    # =====================================================

    st.title("📥 Import Holdings")

    st.write(
        "Add one or more holdings files to the import basket. "
        "PMPH will analyze all added files and combine the "
        "validated holdings into one universal portfolio view."
    )

    st.info(
        "Broker selection is not required. "
        "PMPH identifies holdings from the financial content "
        "and structure of each file."
    )

    st.markdown("---")

    # =====================================================
    # ADD FILE
    # =====================================================

    st.markdown("### 1. Add Holdings File")

    uploaded_file = st.file_uploader(
        "Browse for a holdings file",
        type=[
            "xlsx",
            "xls",
            "csv",
        ],
        accept_multiple_files=False,
        key="holdings_single_file_uploader",
        help=(
            "Choose one file. Add it to the basket, "
            "then browse again to add another file."
        ),
    )

    add_col, info_col = st.columns(
        [
            1,
            3,
        ]
    )

    with add_col:

        add_clicked = st.button(
            "➕ Add File",
            disabled=(
                uploaded_file is None
            ),
            use_container_width=True,
        )

    with info_col:

        if uploaded_file is not None:

            st.write(
                f"Selected: **{uploaded_file.name}**"
            )

    if add_clicked:

        add_file_to_basket(
            uploaded_file
        )

        st.success(
            f"{uploaded_file.name} added to "
            "the import basket."
        )

    # =====================================================
    # FILE BASKET
    # =====================================================

    st.markdown("---")

    st.markdown(
        "### 2. Import Basket"
    )

    basket = (
        st.session_state.holdings_file_basket
    )

    if not basket:

        st.warning(
            "No files have been added yet."
        )

        return

    st.write(
        f"Files currently in basket: "
        f"**{len(basket)}**"
    )

    file_keys = list(
        basket.keys()
    )

    for index, file_key in enumerate(
        file_keys,
        start=1,
    ):

        file_data = basket[
            file_key
        ]

        file_col, size_col, remove_col = (
            st.columns(
                [
                    5,
                    2,
                    1,
                ]
            )
        )

        with file_col:

            st.write(
                f"**{index}. "
                f"{file_data['name']}**"
            )

        with size_col:

            st.write(
                f"{file_data['size']:,} bytes"
            )

        with remove_col:

            remove_clicked = st.button(
                "Remove",
                key=(
                    f"remove_"
                    f"{index}_"
                    f"{file_data['size']}"
                ),
                use_container_width=True,
            )

            if remove_clicked:

                remove_file_from_basket(
                    file_key
                )

                st.rerun()

    st.markdown("")

    analyze_col, clear_col = st.columns(
        [
            3,
            1,
        ]
    )

    with analyze_col:

        analyze_clicked = st.button(
            "🔍 Analyze All Files",
            type="primary",
            use_container_width=True,
        )

    with clear_col:

        clear_clicked = st.button(
            "Clear Basket",
            use_container_width=True,
        )

        if clear_clicked:

            clear_file_basket()

            st.rerun()

    if analyze_clicked:

        st.session_state.holdings_analysis_requested = True

    if not (
        st.session_state.holdings_analysis_requested
    ):

        st.info(
            "Add all required holdings files, "
            "then click **Analyze All Files**."
        )

        return

    # =====================================================
    # UNIVERSAL ENGINES
    # =====================================================

    reader = UniversalHoldingsReader()

    validator = HoldingsValidator()

    file_results = []

    all_validation_results = []

    temporary_files = []

    # =====================================================
    # ANALYZE BASKET
    # =====================================================

    st.markdown("---")

    st.markdown(
        "### 3. Universal File Analysis"
    )

    try:

        with st.spinner(
            f"Analyzing {len(basket)} "
            "holdings file(s)."
        ):

            for (
                file_key,
                file_data,
            ) in basket.items():

                file_name = (
                    file_data[
                        "name"
                    ]
                )

                file_result = {
                    "file_key":
                        file_key,

                    "file_name":
                        file_name,

                    "status":
                        "FAILED",

                    "sheet":
                        "",

                    "confidence":
                        "LOW",

                    "extracted":
                        0,

                    "validated":
                        0,

                    "failed":
                        0,

                    "message":
                        "",

                    "mapping":
                        {},
                }

                try:

                    # -------------------------------------
                    # Temporary local file
                    # -------------------------------------

                    extension = (
                        os.path.splitext(
                            file_name
                        )[1]
                    )

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=extension,
                    ) as temp_file:

                        temp_file.write(
                            file_data[
                                "bytes"
                            ]
                        )

                        temp_path = (
                            temp_file.name
                        )

                    temporary_files.append(
                        temp_path
                    )

                    # -------------------------------------
                    # Content detection
                    # -------------------------------------

                    detection = reader.inspect(
                        temp_path
                    )

                    file_result[
                        "sheet"
                    ] = (
                        detection.get(
                            "sheet_name"
                        )
                        or "Not Detected"
                    )

                    file_result[
                        "confidence"
                    ] = detection.get(
                        "confidence",
                        "LOW"
                    )

                    file_result[
                        "mapping"
                    ] = detection.get(
                        "mapping",
                        {}
                    )

                    if not detection.get(
                        "detected",
                        False
                    ):

                        file_result[
                            "message"
                        ] = (
                            "A reliable holdings "
                            "table was not detected."
                        )

                        file_results.append(
                            file_result
                        )

                        continue

                    # -------------------------------------
                    # Universal extraction
                    # -------------------------------------

                    (
                        detection,
                        holdings,
                    ) = reader.read(
                        temp_path
                    )

                    file_result[
                        "extracted"
                    ] = len(
                        holdings
                    )

                    if not holdings:

                        file_result[
                            "message"
                        ] = (
                            "Holdings table detected, "
                            "but no holdings extracted."
                        )

                        file_results.append(
                            file_result
                        )

                        continue

                    # -------------------------------------
                    # Financial validation
                    # -------------------------------------

                    validation_results = (
                        validator.validate_holdings(
                            holdings
                        )
                    )

                    valid_count = sum(
                        1
                        for result
                        in validation_results
                        if result.is_valid
                    )

                    failed_count = (
                        len(
                            validation_results
                        )
                        - valid_count
                    )

                    file_result[
                        "validated"
                    ] = valid_count

                    file_result[
                        "failed"
                    ] = failed_count

                    # -------------------------------------
                    # Preserve source traceability
                    # -------------------------------------

                    for result in (
                        validation_results
                    ):

                        all_validation_results.append(
                            {
                                "file_key":
                                    file_key,

                                "source_file":
                                    file_name,

                                "source_sheet":
                                    detection.get(
                                        "sheet_name",
                                        ""
                                    ),

                                "table_confidence":
                                    detection.get(
                                        "confidence",
                                        "LOW"
                                    ),

                                "validation":
                                    result,
                            }
                        )

                    # -------------------------------------
                    # File status
                    # -------------------------------------

                    if (
                        valid_count
                        == len(
                            validation_results
                        )
                        and valid_count > 0
                    ):

                        file_result[
                            "status"
                        ] = "SUCCESS"

                        file_result[
                            "message"
                        ] = (
                            "All holdings validated."
                        )

                    elif valid_count > 0:

                        file_result[
                            "status"
                        ] = "REVIEW"

                        file_result[
                            "message"
                        ] = (
                            "Some holdings require review."
                        )

                    else:

                        file_result[
                            "status"
                        ] = "FAILED"

                        file_result[
                            "message"
                        ] = (
                            "No holdings passed validation."
                        )

                    file_results.append(
                        file_result
                    )

                except Exception as error:

                    file_result[
                        "message"
                    ] = str(
                        error
                    )

                    file_results.append(
                        file_result
                    )

        # =================================================
        # FILE SUMMARY
        # =================================================

        summary_rows = []

        for result in file_results:

            summary_rows.append(
                {
                    "File":
                        result[
                            "file_name"
                        ],

                    "Status":
                        result[
                            "status"
                        ],

                    "Sheet":
                        result[
                            "sheet"
                        ],

                    "Confidence":
                        result[
                            "confidence"
                        ],

                    "Extracted":
                        result[
                            "extracted"
                        ],

                    "Validated":
                        result[
                            "validated"
                        ],

                    "Failed":
                        result[
                            "failed"
                        ],

                    "Message":
                        result[
                            "message"
                        ],
                }
            )

        st.dataframe(
            pd.DataFrame(
                summary_rows
            ),
            use_container_width=True,
            hide_index=True,
        )

        # =================================================
        # COMBINED COUNTS
        # =================================================

        valid_results = [
            item
            for item
            in all_validation_results
            if item[
                "validation"
            ].is_valid
        ]

        failed_results = [
            item
            for item
            in all_validation_results
            if not item[
                "validation"
            ].is_valid
        ]

        successful_files = sum(
            1
            for result
            in file_results
            if result[
                "status"
            ] == "SUCCESS"
        )

        st.markdown("---")

        st.markdown(
            "### 4. Combined Import Status"
        )

        (
            files_col,
            success_col,
            found_col,
            valid_col,
            failed_col,
        ) = st.columns(5)

        files_col.metric(
            "Files Added",
            len(
                basket
            ),
        )

        success_col.metric(
            "Files Successful",
            successful_files,
        )

        found_col.metric(
            "Holdings Found",
            len(
                all_validation_results
            ),
        )

        valid_col.metric(
            "Validated",
            len(
                valid_results
            ),
        )

        failed_col.metric(
            "Failed",
            len(
                failed_results
            ),
        )

        # =================================================
        # DETECTION DETAILS
        # =================================================

        with st.expander(
            "View Detection Details"
        ):

            for result in file_results:

                st.markdown(
                    f"#### "
                    f"{result['file_name']}"
                )

                st.write(
                    f"Status: "
                    f"**{result['status']}**"
                )

                st.write(
                    f"Sheet: "
                    f"**{result['sheet']}**"
                )

                st.write(
                    f"Confidence: "
                    f"**{result['confidence']}**"
                )

                mapping = (
                    result[
                        "mapping"
                    ]
                )

                if mapping:

                    mapping_rows = []

                    for (
                        standard_field,
                        details,
                    ) in mapping.items():

                        mapping_rows.append(
                            {
                                "Source Column":
                                    details[
                                        "original_name"
                                    ],

                                "PMPH Field":
                                    standard_field,
                            }
                        )

                    st.dataframe(
                        pd.DataFrame(
                            mapping_rows
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )

                else:

                    st.write(
                        "No reliable mapping detected."
                    )

        # =================================================
        # STOP IF NO VALID HOLDINGS
        # =================================================

        if not valid_results:

            st.error(
                "No validated holdings are "
                "available for preview."
            )

            return

        # =================================================
        # MASTER PREVIEW
        # =================================================

        preview_rows = []

        for item in (
            all_validation_results
        ):

            result = item[
                "validation"
            ]

            holding = (
                result.holding
            )

            preview_rows.append(
                {
                    "Source File":
                        item[
                            "source_file"
                        ],

                    "Source Sheet":
                        item[
                            "source_sheet"
                        ],

                    "Status":
                        (
                            "VALID"
                            if result.is_valid
                            else "REVIEW"
                        ),

                    "Confidence":
                        result.confidence,

                    "Asset Type":
                        holding.asset_type,

                    "Symbol":
                        holding.symbol,

                    "Name":
                        holding.name,

                    "ISIN":
                        holding.isin,

                    "Quantity":
                        holding.quantity,

                    "Average Price":
                        holding.average_price,

                    "Current Price":
                        holding.current_price,

                    "Invested Value":
                        holding.invested_value,

                    "Current Value":
                        holding.current_value,

                    "Profit / Loss":
                        holding.profit_loss,

                    "P/L %":
                        holding.profit_loss_percent,
                }
            )

        preview_df = pd.DataFrame(
            preview_rows
        )

        # =================================================
        # PORTFOLIO TOTALS
        # =================================================

        total_invested = sum(
            item[
                "validation"
            ].holding.invested_value
            for item
            in valid_results
        )

        total_current = sum(
            item[
                "validation"
            ].holding.current_value
            for item
            in valid_results
        )

        total_profit_loss = (
            total_current
            - total_invested
        )

        if total_invested:

            total_return = (
                total_profit_loss
                / total_invested
                * 100
            )

        else:

            total_return = 0.0

        st.markdown("---")

        st.markdown(
            "### 5. Combined Portfolio Summary"
        )

        (
            invested_col,
            current_col,
            profit_col,
            return_col,
        ) = st.columns(4)

        invested_col.metric(
            "Invested Value",
            f"₹{total_invested:,.2f}",
        )

        current_col.metric(
            "Current Value",
            f"₹{total_current:,.2f}",
        )

        profit_col.metric(
            "Profit / Loss",
            f"₹{total_profit_loss:,.2f}",
        )

        return_col.metric(
            "Return",
            f"{total_return:.2f}%",
        )

        # =================================================
        # UNIVERSAL MASTER TABLE
        # =================================================

        st.markdown("---")

        st.markdown(
            "### 6. Master Universal Holdings Preview"
        )

        st.dataframe(
            preview_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Quantity":
                    st.column_config.NumberColumn(
                        format="%.4f"
                    ),

                "Average Price":
                    st.column_config.NumberColumn(
                        format="₹%.2f"
                    ),

                "Current Price":
                    st.column_config.NumberColumn(
                        format="₹%.2f"
                    ),

                "Invested Value":
                    st.column_config.NumberColumn(
                        format="₹%.2f"
                    ),

                "Current Value":
                    st.column_config.NumberColumn(
                        format="₹%.2f"
                    ),

                "Profit / Loss":
                    st.column_config.NumberColumn(
                        format="₹%.2f"
                    ),

                "P/L %":
                    st.column_config.NumberColumn(
                        format="%.2f%%"
                    ),
            },
        )

        # =================================================
        # DUPLICATE SECURITY AWARENESS
        # =================================================

        valid_preview_rows = []

        for item in valid_results:

            holding = (
                item[
                    "validation"
                ].holding
            )

            isin = (
                holding.isin
                or ""
            ).strip().upper()

            symbol = (
                holding.symbol
                or ""
            ).strip().upper()

            if isin:

                security_key = (
                    f"ISIN:{isin}"
                )

            else:

                security_key = (
                    f"SYMBOL:{symbol}"
                )

            valid_preview_rows.append(
                {
                    "Source File":
                        item[
                            "source_file"
                        ],

                    "Symbol":
                        holding.symbol,

                    "ISIN":
                        holding.isin,

                    "Security Key":
                        security_key,
                }
            )

        duplicate_df = pd.DataFrame(
            valid_preview_rows
        )

        if not duplicate_df.empty:

            duplicate_mask = (
                duplicate_df.duplicated(
                    subset=[
                        "Security Key"
                    ],
                    keep=False,
                )
            )

            duplicate_rows = (
                duplicate_df[
                    duplicate_mask
                ]
            )

            if not duplicate_rows.empty:

                st.warning(
                    "The same security appears in more "
                    "than one uploaded file. PMPH has kept "
                    "them separate to prevent accidental "
                    "merging of different accounts or owners."
                )

                st.dataframe(
                    duplicate_rows.drop(
                        columns=[
                            "Security Key"
                        ]
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

        # =================================================
        # FAILED HOLDINGS
        # =================================================

        if failed_results:

            with st.expander(
                "View Holdings Requiring Review"
            ):

                for item in failed_results:

                    result = (
                        item[
                            "validation"
                        ]
                    )

                    st.markdown(
                        f"#### "
                        f"{result.holding.symbol}"
                    )

                    st.write(
                        f"Source: "
                        f"{item['source_file']}"
                    )

                    for error in (
                        result.errors
                    ):

                        st.write(
                            f"- {error}"
                        )

        # =================================================
        # FINAL VALIDATION STATUS
        # =================================================

        st.markdown("---")

        if (
            len(
                valid_results
            )
            == len(
                all_validation_results
            )
            and successful_files
            == len(
                basket
            )
        ):

            st.success(
                f"All {len(valid_results)} "
                f"holding(s) from "
                f"{len(basket)} file(s) "
                "were successfully extracted "
                "and financially validated."
            )

        else:

            st.warning(
                "Validated holdings are shown above. "
                "Any failed files or holdings have "
                "not been treated as safely importable."
            )

        # =================================================
        # ACCOUNT ASSIGNMENT + DATABASE IMPORT
        # =================================================

        st.markdown("---")

        st.markdown(
            "### 7. Assign Files to Portfolio Accounts"
        )

        st.write(
            "Assign each successfully analyzed holdings file "
            "to the correct owner, platform/broker, and account."
        )

        st.info(
            "Each file is assigned independently. "
            "This prevents holdings belonging to different "
            "family members or broker accounts from being "
            "accidentally merged."
        )

        import_service = (
            PortfolioImportService(
                "data/pmph_portfolio.db"
            )
        )

        # -------------------------------------------------
        # Group validation results by original basket file
        # -------------------------------------------------

        validations_by_file = {}

        for item in all_validation_results:

            item_file_key = (
                item[
                    "file_key"
                ]
            )

            if (
                item_file_key
                not in validations_by_file
            ):

                validations_by_file[
                    item_file_key
                ] = []

            validations_by_file[
                item_file_key
            ].append(
                item[
                    "validation"
                ]
            )

        assignment_results = {}

        importable_files = []

        # -------------------------------------------------
        # Show assignment controls
        # -------------------------------------------------

        for index, (
            file_key,
            file_data,
        ) in enumerate(
            basket.items(),
            start=1,
        ):

            file_validations = (
                validations_by_file.get(
                    file_key,
                    []
                )
            )

            valid_file_holdings = [
                result
                for result
                in file_validations
                if result.is_valid
            ]

            if not valid_file_holdings:

                continue

            importable_files.append(
                file_key
            )

            st.markdown("---")

            st.markdown(
                f"#### File {index}: "
                f"{file_data['name']}"
            )

            st.write(
                f"Validated holdings ready: "
                f"**{len(valid_file_holdings)}**"
            )

            # Internal identity is unique even if two
            # uploaded files have the same visible filename.

            assignment_identity = (
                f"{file_data['name']}"
                f"__{file_data['size']}"
                f"__{index}"
            )

            assignment = (
                show_account_assignment(
                    file_name=(
                        assignment_identity
                    ),
                    import_service=(
                        import_service
                    ),
                )
            )

            assignment_results[
                file_key
            ] = assignment

        # -------------------------------------------------
        # Check all assignments
        # -------------------------------------------------

        all_files_assigned = (
            bool(
                importable_files
            )
            and all(
                assignment_results.get(
                    file_key,
                    {}
                ).get(
                    "ready",
                    False
                )
                for file_key
                in importable_files
            )
        )

        # =================================================
        # FINAL IMPORT CONFIRMATION + IMPACT PREVIEW
        # =================================================

        st.markdown("---")

        st.markdown(
            "### 8. Pre-Import Impact & Final Confirmation"
        )

        if not all_files_assigned:

            st.warning(
                "Assign every importable file to a "
                "portfolio account before continuing."
            )

        else:

            # =============================================
            # SAFETY CHECK:
            # MORE THAN ONE FULL FILE FOR SAME ACCOUNT
            # =============================================

            full_account_files = {}

            for file_key in importable_files:

                assignment = (
                    assignment_results[
                        file_key
                    ]
                )

                account = (
                    assignment[
                        "account"
                    ]
                )

                mode = (
                    assignment[
                        "mode"
                    ]
                )

                if mode != "FULL":
                    continue

                account_id = (
                    account.account_id
                )

                if (
                    account_id
                    not in full_account_files
                ):

                    full_account_files[
                        account_id
                    ] = []

                full_account_files[
                    account_id
                ].append(
                    basket[
                        file_key
                    ][
                        "name"
                    ]
                )

            duplicate_full_accounts = {
                account_id:
                    file_names

                for (
                    account_id,
                    file_names,
                ) in (
                    full_account_files.items()
                )

                if len(
                    file_names
                ) > 1
            }

            configuration_safe = (
                not duplicate_full_accounts
            )

            if not configuration_safe:

                st.error(
                    "Unsafe FULL-statement configuration "
                    "detected."
                )

                st.write(
                    "More than one FULL statement has been "
                    "assigned to the same portfolio account. "
                    "PMPH will not allow this because one "
                    "FULL statement could remove holdings "
                    "contained in another file."
                )

                for (
                    account_id,
                    file_names,
                ) in (
                    duplicate_full_accounts.items()
                ):

                    account_name = (
                        account_id
                    )

                    for file_key in (
                        importable_files
                    ):

                        assignment = (
                            assignment_results[
                                file_key
                            ]
                        )

                        account = (
                            assignment[
                                "account"
                            ]
                        )

                        if (
                            account.account_id
                            == account_id
                        ):

                            account_name = (
                                account
                                .display_name()
                            )

                            break

                    st.markdown(
                        f"**{account_name}**"
                    )

                    for file_name in (
                        file_names
                    ):

                        st.write(
                            f"- {file_name}"
                        )

                st.warning(
                    "Change one or more of these files "
                    "to PARTIAL, or assign them to the "
                    "correct separate accounts."
                )

            # =============================================
            # READ-ONLY IMPACT PREVIEW
            # =============================================

            preview_results = {}

            preview_rows = []

            removal_rows = []

            addition_rows = []

            update_rows = []

            preview_failed = False

            if configuration_safe:

                for file_key in (
                    importable_files
                ):

                    file_data = (
                        basket[
                            file_key
                        ]
                    )

                    assignment = (
                        assignment_results[
                            file_key
                        ]
                    )

                    account = (
                        assignment[
                            "account"
                        ]
                    )

                    mode = (
                        assignment[
                            "mode"
                        ]
                    )

                    file_validations = (
                        validations_by_file.get(
                            file_key,
                            []
                        )
                    )

                    preview = (
                        import_service
                        .preview_validated_holdings(
                            account=account,

                            validation_results=(
                                file_validations
                            ),

                            mode=mode,

                            source_file=(
                                file_data[
                                    "name"
                                ]
                            ),
                        )
                    )

                    preview_results[
                        file_key
                    ] = preview

                    if not preview.success:

                        preview_failed = True

                    preview_rows.append(
                        {
                            "Source File":
                                file_data[
                                    "name"
                                ],

                            "Portfolio Account":
                                (
                                    account
                                    .display_name()
                                ),

                            "Mode":
                                mode,

                            "Incoming":
                                (
                                    preview
                                    .incoming_count
                                ),

                            "Added":
                                (
                                    preview
                                    .added_count
                                ),

                            "Updated":
                                (
                                    preview
                                    .updated_count
                                ),

                            "Removed":
                                (
                                    preview
                                    .removed_count
                                ),

                            "Unchanged":
                                (
                                    preview
                                    .unchanged_count
                                ),

                            "Preview":
                                (
                                    "READY"
                                    if preview.success
                                    else "FAILED"
                                ),
                        }
                    )

                    # -------------------------------------
                    # Exact additions
                    # -------------------------------------

                    for impact in (
                        preview.added
                    ):

                        addition_rows.append(
                            {
                                "Source File":
                                    file_data[
                                        "name"
                                    ],

                                "Account":
                                    (
                                        account
                                        .display_name()
                                    ),

                                "Symbol":
                                    impact.symbol,

                                "ISIN":
                                    impact.isin,

                                "New Quantity":
                                    (
                                        impact
                                        .new_quantity
                                    ),
                            }
                        )

                    # -------------------------------------
                    # Exact updates
                    # -------------------------------------

                    for impact in (
                        preview.updated
                    ):

                        update_rows.append(
                            {
                                "Source File":
                                    file_data[
                                        "name"
                                    ],

                                "Account":
                                    (
                                        account
                                        .display_name()
                                    ),

                                "Symbol":
                                    impact.symbol,

                                "ISIN":
                                    impact.isin,

                                "Old Quantity":
                                    (
                                        impact
                                        .old_quantity
                                    ),

                                "New Quantity":
                                    (
                                        impact
                                        .new_quantity
                                    ),
                            }
                        )

                    # -------------------------------------
                    # Exact removals
                    # -------------------------------------

                    for impact in (
                        preview.removed
                    ):

                        removal_rows.append(
                            {
                                "Source File":
                                    file_data[
                                        "name"
                                    ],

                                "Account":
                                    (
                                        account
                                        .display_name()
                                    ),

                                "Symbol":
                                    impact.symbol,

                                "ISIN":
                                    impact.isin,

                                "Current Quantity":
                                    (
                                        impact
                                        .old_quantity
                                    ),
                            }
                        )

                # =========================================
                # IMPACT SUMMARY
                # =========================================

                st.markdown(
                    "#### Read-Only Import Impact"
                )

                st.caption(
                    "Nothing has been written to the "
                    "portfolio database by this preview."
                )

                st.dataframe(
                    pd.DataFrame(
                        preview_rows
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

                total_preview_added = sum(
                    row[
                        "Added"
                    ]
                    for row
                    in preview_rows
                )

                total_preview_updated = sum(
                    row[
                        "Updated"
                    ]
                    for row
                    in preview_rows
                )

                total_preview_removed = sum(
                    row[
                        "Removed"
                    ]
                    for row
                    in preview_rows
                )

                total_preview_unchanged = sum(
                    row[
                        "Unchanged"
                    ]
                    for row
                    in preview_rows
                )

                (
                    preview_add_col,
                    preview_update_col,
                    preview_remove_col,
                    preview_unchanged_col,
                ) = st.columns(4)

                preview_add_col.metric(
                    "Will Add",
                    total_preview_added,
                )

                preview_update_col.metric(
                    "Will Update",
                    total_preview_updated,
                )

                preview_remove_col.metric(
                    "Will Remove",
                    total_preview_removed,
                )

                preview_unchanged_col.metric(
                    "Unchanged",
                    total_preview_unchanged,
                )

                # =========================================
                # EXACT ADDITIONS
                # =========================================

                if addition_rows:

                    with st.expander(
                        "View Holdings That Will Be Added"
                    ):

                        st.dataframe(
                            pd.DataFrame(
                                addition_rows
                            ),
                            use_container_width=True,
                            hide_index=True,
                        )

                # =========================================
                # EXACT UPDATES
                # =========================================

                if update_rows:

                    with st.expander(
                        "View Holdings That Will Be Updated"
                    ):

                        st.dataframe(
                            pd.DataFrame(
                                update_rows
                            ),
                            use_container_width=True,
                            hide_index=True,
                        )

                # =========================================
                # EXACT REMOVALS
                # =========================================

                if removal_rows:

                    st.error(
                        "FULL synchronization will remove "
                        "the holdings shown below from the "
                        "current PMPH portfolio database."
                    )

                    st.dataframe(
                        pd.DataFrame(
                            removal_rows
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )

                else:

                    st.success(
                        "The current preview contains no "
                        "holding removals."
                    )

                # =========================================
                # PREVIEW ERRORS
                # =========================================

                if preview_failed:

                    st.error(
                        "One or more import previews failed. "
                        "Real database import has been blocked."
                    )

                    for file_key in (
                        importable_files
                    ):

                        preview = (
                            preview_results.get(
                                file_key
                            )
                        )

                        if (
                            preview is None
                            or preview.success
                        ):

                            continue

                        file_name = (
                            basket[
                                file_key
                            ][
                                "name"
                            ]
                        )

                        st.markdown(
                            f"**{file_name}**"
                        )

                        for error in (
                            preview.errors
                        ):

                            st.write(
                                f"- {error}"
                            )

            # =============================================
            # FINAL CONFIRMATION
            # =============================================

            import_ready = (
                configuration_safe
                and not preview_failed
                and bool(
                    preview_rows
                )
            )

            if import_ready:

                st.markdown("---")

                st.markdown(
                    "#### Final Authorization"
                )

                if removal_rows:

                    st.warning(
                        "This import includes one or more "
                        "holding removals. Review the removal "
                        "table carefully before confirming."
                    )

                else:

                    st.info(
                        "The impact preview is ready. "
                        "Review the account assignments and "
                        "changes before confirming."
                    )

                confirm_import = (
                    st.checkbox(
                        (
                            "I have reviewed the pre-import "
                            "impact and confirm that each file "
                            "is assigned to the correct account "
                            "with the correct FULL/PARTIAL mode."
                        ),
                        key=(
                            "confirm_real_holdings_import"
                        ),
                    )
                )

                # Extra confirmation when destructive
                # FULL removals are present.

                removal_confirmed = True

                if removal_rows:

                    removal_confirmed = (
                        st.checkbox(
                            (
                                "I specifically confirm the "
                                "holding removal(s) shown above."
                            ),
                            key=(
                                "confirm_holdings_removals"
                            ),
                        )
                    )

                import_clicked = (
                    st.button(
                        (
                            "💾 Confirm & Import "
                            "Validated Holdings"
                        ),
                        type="primary",
                        disabled=(
                            not confirm_import
                            or not removal_confirmed
                        ),
                        use_container_width=True,
                    )
                )

                # =========================================
                # PROTECTED REAL DATABASE BATCH IMPORT
                # =========================================

                if import_clicked:

                    batch_items = []

                    for file_key in importable_files:

                        file_data = basket[file_key]
                        assignment = assignment_results[file_key]

                        batch_items.append(
                            BatchImportItem(
                                source_file=file_data["name"],
                                account=assignment["account"],
                                validation_results=validations_by_file.get(
                                    file_key,
                                    [],
                                ),
                                mode=assignment["mode"],
                            )
                        )

                    batch_service = PortfolioBatchImportService(
                        portfolio_import_service=import_service,
                        database_path="data/pmph_portfolio.db",
                        backup_directory="data/backups",
                    )

                    with st.spinner(
                        "Creating a verified safety backup "
                        "and importing the confirmed batch..."
                    ):

                        batch_result = batch_service.import_batch(
                            batch_items
                        )

                    st.markdown("---")
                    st.markdown("### 9. Protected Import Result")

                    if batch_result.backup_created:

                        st.success(
                            "Verified pre-import database "
                            "backup created successfully."
                        )

                        st.code(batch_result.backup_path)

                    else:

                        st.error(
                            "No verified pre-import backup "
                            "was created. Database writes "
                            "were blocked."
                        )

                    import_results = []

                    for index, result in enumerate(
                        batch_result.import_results
                    ):

                        source_file = (
                            batch_items[index].source_file
                            if index < len(batch_items)
                            else ""
                        )

                        import_results.append(
                            {
                                "File": source_file,
                                "Account": result.account_display_name,
                                "Mode": result.mode,
                                "Success": result.success,
                                "Incoming": result.incoming_count,
                                "Added": result.added_count,
                                "Updated": result.updated_count,
                                "Removed": result.removed_count,
                                "Unchanged": result.unchanged_count,
                                "Errors": "; ".join(result.errors),
                            }
                        )

                    if import_results:

                        st.dataframe(
                            pd.DataFrame(import_results),
                            width="stretch",
                            hide_index=True,
                        )

                    total_added = sum(
                        row["Added"]
                        for row in import_results
                    )

                    total_updated = sum(
                        row["Updated"]
                        for row in import_results
                    )

                    total_removed = sum(
                        row["Removed"]
                        for row in import_results
                    )

                    total_unchanged = sum(
                        row["Unchanged"]
                        for row in import_results
                    )

                    (
                        added_col,
                        updated_col,
                        removed_col,
                        unchanged_col,
                    ) = st.columns(4)

                    added_col.metric("Added", total_added)
                    updated_col.metric("Updated", total_updated)
                    removed_col.metric("Removed", total_removed)
                    unchanged_col.metric(
                        "Unchanged",
                        total_unchanged,
                    )

                    st.write(
                        "Files completed: "
                        f"**{batch_result.completed_files}"
                        f"/{batch_result.total_files}**"
                    )

                    if batch_result.errors:

                        st.error(
                            "The protected batch did not "
                            "complete successfully."
                        )

                        for error in batch_result.errors:

                            st.write(f"- {error}")

                        if batch_result.backup_created:

                            st.warning(
                                "The verified pre-import backup "
                                "has been preserved for explicit "
                                "recovery. PMPH did not "
                                "automatically restore it."
                            )

                    elif batch_result.success:

                        st.success(
                            "The complete confirmed batch was "
                            "successfully imported into the "
                            "PMPH portfolio database."
                        )

                        st.info(
                            "The backup shown above is the "
                            "recovery point immediately before "
                            "this import."
                        )

                    else:

                        st.error(
                            "The protected batch import "
                            "did not complete."
                        )

    finally:

        # =================================================
        # CLEAN TEMPORARY FILES
        # =================================================

        for temp_path in temporary_files:

            if temp_path and os.path.exists(temp_path):

                try:
                    os.remove(temp_path)
                except OSError:
                    pass
