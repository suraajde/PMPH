import streamlit as st


def show():

    st.title("📥 Import Holdings")

    st.info("Import module will be developed in the next sprint.")

    st.markdown("---")

    st.write("Supported Brokers")

    brokers = [
        "Groww",
        "Zerodha",
        "HDFC Sky",
        "ProStocks",
        "Dhan"
    ]

    for broker in brokers:
        st.checkbox(broker, disabled=True)

    st.button("Import Holdings", disabled=True)