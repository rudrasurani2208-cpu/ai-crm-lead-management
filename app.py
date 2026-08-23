import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="AI CRM & Lead Management",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI CRM & Lead Management System")
st.write("Manage leads, track sales opportunities, and prioritize customers using AI-based lead scoring.")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Add Lead", "Lead Database", "Sales Pipeline"]
)

if page == "Dashboard":
    st.header("Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Leads", "0")
    col2.metric("Hot Leads", "0")
    col3.metric("Converted Leads", "0")
    col4.metric("Conversion Rate", "0%")
