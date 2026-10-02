import streamlit as st

st.set_page_config(
    page_title="E-commerce Cloud Analytics",
    page_icon="📊",
    layout="wide",
)

st.title("E-commerce Cloud Analytics")
st.caption("An independent analytics portfolio by Gia Bao Ly")

st.success("Streamlit cloud deployment is working.")

st.subheader("Project purpose")
st.write(
    "Analyze historical e-commerce sales, product and regional "
    "performance, delivery experience, and customer purchasing behavior."
)

st.info(
    "The project is under development. "
    "No dataset has been loaded into this app yet."
)

st.link_button(
    "View GitHub repository",
    "https://github.com/blvckroom/ecommerce-cloud-analytics",
)
