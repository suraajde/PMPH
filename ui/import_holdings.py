import os
import tempfile

import pandas as pd
import streamlit as st

from services.holdings_validator import HoldingsValidator
from services.universal_holdings_reader import UniversalHoldingsReader


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

        st.write(
            "Browse for a file above, click "
            "**Add File**, then repeat for any "
            "additional holdings files."
        )

        return

    st.write(
        f"Files currently added: "
        f"**{len(basket)}**"
    )

    # -----------------------------------------------------
    # Display files in basket
    # -----------------------------------------------------

    for index, (
        file_key,
        file_data,
    ) in enumerate(
        list(
            basket.items()
        ),
        start=1,
    ):

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

            size_kb = (
                file_data[
                    "size"
                ]
                / 1024
            )

            st.write(
                f"{size_kb:,.1f} KB"
            )

        with remove_col:

            if st.button(
                "Remove",
                key=(
                    f"remove_holding_file_"
                    f"{index}_"
                    f"{file_data['name']}"
                ),
            ):

                remove_file_from_basket(
                    file_key
                )

                st.rerun()

    # =====================================================
    # BASKET CONTROLS
    # =====================================================

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

        if st.button(
            "Clear All",
            use_container_width=True,
        ):

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
            "holdings file(s)..."
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

        valid_rows = []

        for item in valid_results:

            holding = (
                item[
                    "validation"
                ].holding
            )

            isin = str(
                holding.isin
                or ""
            ).strip()

            symbol = str(
                holding.symbol
                or ""
            ).strip()

            security_key = (
                f"ISIN:{isin}"
                if isin
                else f"SYMBOL:{symbol}"
            )

            valid_rows.append(
                {
                    "Security Key":
                        security_key,

                    "Source File":
                        item[
                            "source_file"
                        ],

                    "Symbol":
                        symbol,

                    "ISIN":
                        isin,

                    "Quantity":
                        holding.quantity,

                    "Invested Value":
                        holding.invested_value,

                    "Current Value":
                        holding.current_value,
                }
            )

        duplicate_df = pd.DataFrame(
            valid_rows
        )

        if not duplicate_df.empty:

            duplicate_rows = (
                duplicate_df[
                    duplicate_df.duplicated(
                        "Security Key",
                        keep=False
                    )
                ]
            )

            if not duplicate_rows.empty:

                st.warning(
                    "The same security appears in "
                    "multiple source rows/files. "
                    "PMPH has kept them separate "
                    "to prevent accidental merging "
                    "of different accounts or owners."
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
        # FINAL STATUS
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
        # DATABASE IMPORT
        # =================================================

        st.button(
            "Import Validated Holdings",
            disabled=True,
            use_container_width=True,
        )

        st.caption(
            "Database import remains disabled for now. "
            "This sprint verifies persistent multi-file "
            "collection, universal extraction, validation, "
            "and combined portfolio preview."
        )

    finally:

        # =================================================
        # CLEAN TEMPORARY FILES
        # =================================================

        for temp_path in (
            temporary_files
        ):

            if (
                temp_path
                and os.path.exists(
                    temp_path
                )
            ):

                try:

                    os.remove(
                        temp_path
                    )

                except OSError:

                    pass