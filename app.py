import streamlit as st

from config import APP_NAME, APP_FULL_NAME, VERSION
from core.database import DatabaseManager

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
# Header
# ---------------------------------------------------------
st.title(APP_FULL_NAME)
st.caption(f"Version {VERSION}")

# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------
st.success("✅ Database initialized successfully.")

st.info("Welcome to PMPH - Portfolio Manager & Portfolio Health")

# ---------------------------------------------------------
# Close Database
# ---------------------------------------------------------
db.close()