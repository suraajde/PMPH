import streamlit as st

from config import APP_NAME, APP_FULL_NAME, VERSION
from core.database import Database

st.set_page_config(
    page_title=APP_NAME,
    page_icon="📊",
    layout="wide"
)

st.title(APP_FULL_NAME)
st.write(f"Version : {VERSION}")

db = Database()
db.connect()

st.success("Database connected successfully.")

db.close()