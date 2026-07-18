import streamlit as st

from config import APP_NAME, APP_FULL_NAME, VERSION
from core.database import DatabaseManager
from core.navigation import Navigation

from ui import dashboard
from ui import import_holdings
from ui import database_view


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title=APP_NAME,
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------------
# Initialize Database
# ---------------------------------------------------------
db = DatabaseManager()
db.initialize_database()

# ---------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------
page = Navigation.sidebar()

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.title(APP_FULL_NAME)
st.caption(f"Version {VERSION}")

st.markdown("---")

# ---------------------------------------------------------
# Page Routing
# ---------------------------------------------------------
if page == "Dashboard":
    dashboard.show()

elif page == "Import Holdings":
    import_holdings.show()

elif page == "Database":
    database_view.show()

# ---------------------------------------------------------
# Close Database
# ---------------------------------------------------------
db.close()