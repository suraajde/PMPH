import streamlit as st


class Navigation:

    @staticmethod
    def sidebar():

        st.sidebar.title("📊 PMPH")

        page = st.sidebar.radio(
            "Navigation",
            [
                "Dashboard",
                "Import Holdings",
                "Database"
            ]
        )

        return page