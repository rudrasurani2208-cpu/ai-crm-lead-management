import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="AI CRM & Lead Management",
    page_icon="📊",
    layout="wide"
)

DATA_FILE = "leads.csv"

# Create CSV file if it doesn't exist
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(
        columns=[
            "name",
            "email",
            "phone",
            "company",
            "source",
            "budget",
            "interest",
            "status"
        ]
    )
    df.to_csv(DATA_FILE, index=False)


def load_leads():
    return pd.read_csv(DATA_FILE)


def save_lead(new_lead):
    df = load_leads()
    df = pd.concat([df, pd.DataFrame([new_lead])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)


st.title("📊 AI CRM & Lead Management System")
st.write(
    "Manage leads, track sales opportunities, "
    "and prioritize customers using AI-based lead scoring."
)

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Dashboard",
        "Add Lead",
        "Lead Database",
        "Sales Pipeline"
    ]
)

if page == "Dashboard":

    st.header("Dashboard")

    leads = load_leads()

    total_leads = len(leads)

    hot_leads = len(
        leads[leads["interest"] >= 8]
    ) if total_leads > 0 else 0

    converted_leads = len(
        leads[leads["status"] == "Closed"]
    ) if total_leads > 0 else 0

    conversion_rate = (
        (converted_leads / total_leads) * 100
        if total_leads > 0
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Leads", total_leads)
    col2.metric("Hot Leads", hot_leads)
    col3.metric("Converted Leads", converted_leads)
    col4.metric("Conversion Rate", f"{conversion_rate:.1f}%")

    if total_leads == 0:
        st.info("Add your first lead to start seeing analytics.")

    else:
        st.subheader("Lead Sources")

        source_data = leads["source"].value_counts()

        st.bar_chart(source_data)


elif page == "Add Lead":

    st.header("Add New Lead")

    with st.form("lead_form"):

        name = st.text_input("Customer Name")

        email = st.text_input("Email")

        phone = st.text_input("Phone Number")

        company = st.text_input("Company")

        source = st.selectbox(
            "Lead Source",
            [
                "Website",
                "Instagram",
                "LinkedIn",
                "Referral",
                "Cold Call",
                "Other"
            ]
        )

        budget = st.number_input(
            "Estimated Budget",
            min_value=0.0,
            step=1000.0
        )

        interest = st.slider(
            "Interest Level",
            1,
            10,
            5
        )

        status = st.selectbox(
            "Lead Status",
            [
                "New",
                "Contacted",
                "Negotiation",
                "Closed"
            ]
        )

        submitted = st.form_submit_button("Add Lead")

        if submitted:

            if name.strip() == "":
                st.error("Please enter the customer's name.")

            else:

                new_lead = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "company": company,
                    "source": source,
                    "budget": budget,
                    "interest": interest,
                    "status": status
                }

                save_lead(new_lead)

                st.success(
                    f"Lead '{name}' added successfully!"
                )


elif page == "Lead Database":

    st.header("Lead Database")

    leads = load_leads()

    if len(leads) == 0:

        st.info("No leads have been added yet.")

    else:

        st.dataframe(
            leads,
            use_container_width=True
        )


elif page == "Sales Pipeline":

    st.header("Sales Pipeline")

    leads = load_leads()

    col1, col2, col3, col4 = st.columns(4)

    stages = [
        ("New", col1),
        ("Contacted", col2),
        ("Negotiation", col3),
        ("Closed", col4)
    ]

    for stage, column in stages:

        with column:

            st.subheader(stage)

            stage_leads = leads[
                leads["status"] == stage
            ]

            if len(stage_leads) == 0:

                st.caption("No leads")

            else:

                for _, lead in stage_leads.iterrows():

                    st.markdown(
                        f"""
                        **{lead['name']}**

                        {lead['company']}

                        Budget: ₹{lead['budget']:,.0f}

                        Interest: {lead['interest']}/10
                        """
                    )

                    st.divider()
