import streamlit as st
import pandas as pd
from supabase import create_client, Client

st.set_page_config(
    page_title="AI CRM & Lead Management",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# SUPABASE CONNECTION
# -----------------------------

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]


@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase: Client = init_supabase()


# -----------------------------
# DATABASE FUNCTIONS
# -----------------------------

def load_leads():
    try:
        response = (
            supabase
            .table("leads")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        data = response.data

        if not data:
            return pd.DataFrame(
                columns=[
                    "id",
                    "created_at",
                    "name",
                    "email",
                    "phone",
                    "company",
                    "source",
                    "budget",
                    "interest",
                    "status",
                    "score",
                    "category"
                ]
            )

        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()


def save_lead(new_lead):
    try:
        supabase.table("leads").insert(new_lead).execute()
        return True

    except Exception as e:
        st.error(f"Could not save lead: {e}")
        return False
def update_lead_status(lead_id, new_status):
    try:
        (
            supabase
            .table("leads")
            .update({"status": new_status})
            .eq("id", int(lead_id))
            .execute()
        )
        return True

    except Exception as e:
        st.error(f"Could not update lead: {e}")
        return False


def delete_lead(lead_id):
    try:
        (
            supabase
            .table("leads")
            .delete()
            .eq("id", int(lead_id))
            .execute()
        )
        return True

    except Exception as e:
        st.error(f"Could not delete lead: {e}")
        return False
def update_followup_notes(lead_id, follow_up_date, notes):
    try:
        (
            supabase
            .table("leads")
            .update({
                "follow_up_date": str(follow_up_date),
                "notes": notes
            })
            .eq("id", int(lead_id))
            .execute()
        )
        return True

    except Exception as e:
        st.error(f"Could not update follow-up details: {e}")
        return False
# -----------------------------
# LEAD SCORING
# -----------------------------

def calculate_lead_score(budget, interest, source):
    score = 0

    # Interest = maximum 50 points
    score += interest * 5

    # Budget = maximum 30 points
    if budget >= 100000:
        score += 30
    elif budget >= 50000:
        score += 20
    elif budget >= 20000:
        score += 10

    # Source = maximum 20 points
    source_points = {
        "Referral": 20,
        "LinkedIn": 15,
        "Website": 15,
        "Instagram": 10,
        "Cold Call": 5,
        "Other": 5
    }

    score += source_points.get(source, 0)

    if score >= 75:
        category = "Hot 🔥"
    elif score >= 50:
        category = "Warm 🟡"
    else:
        category = "Cold ❄️"

    return score, category


# -----------------------------
# APP HEADER
# -----------------------------

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
        "Manage Leads",
        "Sales Pipeline"
    ]
)


# -----------------------------
# DASHBOARD
# -----------------------------

if page == "Dashboard":

    st.header("Dashboard")

    leads = load_leads()

    total_leads = len(leads)

    if total_leads > 0:

        hot_leads = len(
            leads[leads["category"] == "Hot 🔥"]
        )

        converted_leads = len(
            leads[leads["status"] == "Closed"]
        )

        conversion_rate = (
            converted_leads / total_leads
        ) * 100

    else:

        hot_leads = 0
        converted_leads = 0
        conversion_rate = 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Leads",
        total_leads
    )

    col2.metric(
        "Hot Leads",
        hot_leads
    )

    col3.metric(
        "Converted Leads",
        converted_leads
    )

    col4.metric(
        "Conversion Rate",
        f"{conversion_rate:.1f}%"
    )

    if total_leads == 0:

        st.info(
            "Add your first lead to start seeing analytics."
        )

    else:

        st.subheader("Lead Sources")

        source_data = (
            leads["source"]
            .value_counts()
        )

        st.bar_chart(source_data)

        st.subheader("Lead Categories")

        category_data = (
            leads["category"]
            .value_counts()
        )

        st.bar_chart(category_data)


# -----------------------------
# ADD LEAD
# -----------------------------

elif page == "Add Lead":

    st.header("Add New Lead")

    with st.form("lead_form"):

        name = st.text_input(
            "Customer Name"
        )

        email = st.text_input(
            "Email"
        )

        phone = st.text_input(
            "Phone Number"
        )

        company = st.text_input(
            "Company"
        )

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

        submitted = st.form_submit_button(
            "Add Lead"
        )

        if submitted:

            if name.strip() == "":

                st.error(
                    "Please enter the customer's name."
                )

            else:

                score, category = calculate_lead_score(
                    budget,
                    interest,
                    source
                )

                new_lead = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "company": company,
                    "source": source,
                    "budget": budget,
                    "interest": interest,
                    "status": status,
                    "score": score,
                    "category": category
                }

                success = save_lead(
                    new_lead
                )

                if success:

                    st.success(
                        f"Lead '{name}' added successfully! "
                        f"Score: {score}/100 — {category}"
                    )


# -----------------------------
# LEAD DATABASE
# -----------------------------

elif page == "Lead Database":

    st.header("Lead Database")

    leads = load_leads()

    if len(leads) == 0:

        st.info(
            "No leads have been added yet."
        )

    else:

        display_columns = [
            "name",
            "company",
            "source",
            "budget",
            "interest",
            "score",
            "category",
            "status"
        ]

        st.dataframe(
            leads[display_columns],
            use_container_width=True,
            hide_index=True
        )


# -----------------------------
# SALES PIPELINE
# -----------------------------
elif page == "Manage Leads":

    st.header("Manage Leads")

    leads = load_leads()

    if len(leads) == 0:
        st.info("No leads available to manage.")

    else:
        lead_options = {
            f"{row['name']} — {row['company']} — ID {row['id']}": row["id"]
            for _, row in leads.iterrows()
        }

        selected_label = st.selectbox(
            "Select Lead",
            list(lead_options.keys())
        )

        selected_id = lead_options[selected_label]

        selected_lead = leads[
            leads["id"] == selected_id
        ].iloc[0]

        st.subheader(selected_lead["name"])

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Company:** {selected_lead['company']}")
            st.write(f"**Email:** {selected_lead['email']}")
            st.write(f"**Phone:** {selected_lead['phone']}")
            st.write(f"**Source:** {selected_lead['source']}")

        with col2:
            st.write(
                f"**Budget:** ₹{float(selected_lead['budget']):,.0f}"
            )
            st.write(
                f"**Interest:** {selected_lead['interest']}/10"
            )
            st.write(
                f"**Score:** {selected_lead['score']}/100"
            )
            st.write(
                f"**Category:** {selected_lead['category']}"
            )

        st.divider()

        st.subheader("Update Lead Status")

        status_options = [
            "New",
            "Contacted",
            "Negotiation",
            "Closed"
        ]

        current_status = selected_lead["status"]

        current_index = (
            status_options.index(current_status)
            if current_status in status_options
            else 0
        )

        new_status = st.selectbox(
            "Lead Status",
            status_options,
            index=current_index
        )

        if st.button("Update Status"):

            success = update_lead_status(
                selected_id,
                new_status
            )

            if success:
                st.success(
                    f"Status updated to {new_status}."
                )
                st.rerun()

        st.divider()
st.subheader("Follow-up & Notes")
st.subheader("Follow-up & Notes")

        existing_date = selected_lead.get("follow_up_date")

        if existing_date:
            try:
                default_followup = datetime.strptime(
                    str(existing_date),
                    "%Y-%m-%d"
                ).date()
            except:
                default_followup = date.today()
        else:
            default_followup = date.today()

        follow_up_date = st.date_input(
            "Follow-up Date",
            value=default_followup
        )

        existing_notes = selected_lead.get("notes")

        if pd.isna(existing_notes):
            existing_notes = ""

        notes = st.text_area(
            "Notes",
            value=str(existing_notes),
            placeholder="Add conversation notes, next steps, customer requirements..."
        )

        if st.button("Save Follow-up Details"):
            success = update_followup_notes(
                selected_id,
                follow_up_date,
                notes
            )

            if success:
                st.success(
                    "Follow-up date and notes saved successfully."
                )
                st.rerun()

        st.divider()

        st.subheader("Delete Lead")
 


        confirm_delete = st.checkbox(
            "I understand this will permanently delete this lead."
        )

        if st.button(
            "Delete Lead",
            disabled=not confirm_delete
        ):

            success = delete_lead(
                selected_id
            )

            if success:
                st.success(
                    "Lead deleted successfully."
                )
                st.rerun()
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

            if len(leads) == 0:

                st.caption(
                    "No leads"
                )

                continue

            stage_leads = leads[
                leads["status"] == stage
            ]

            if len(stage_leads) == 0:

                st.caption(
                    "No leads"
                )

            else:

                for _, lead in stage_leads.iterrows():

                    st.markdown(
                        f"""
                        **{lead['name']}**

                        {lead['company']}

                        Budget: ₹{float(lead['budget']):,.0f}

                        Interest: {lead['interest']}/10

                        Score: {lead['score']}/100

                        {lead['category']}
                        """
                    )

                    st.divider()
