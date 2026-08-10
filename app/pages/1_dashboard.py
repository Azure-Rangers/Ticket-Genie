from __future__ import annotations

import streamlit as st

from app.services.tickets import (
    get_sample_tickets,
    summarize_ticket_queue,
)


# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="Help & Support | Ticket-Genie",
    page_icon="🎫",
    layout="wide",
)


# =========================================================
# STYLING
# =========================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #f6f8f7;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #173f35;
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    /* Main title */
    .main-title {
        font-size: 32px;
        font-weight: 700;
        color: #173f35;
        margin-bottom: 5px;
    }

    .main-subtitle {
        font-size: 15px;
        color: #66736f;
        margin-bottom: 25px;
    }

    /* Cards */
    .help-card {
        background-color: white;
        border: 1px solid #e3e9e6;
        border-radius: 12px;
        padding: 20px;
        min-height: 130px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    .help-icon {
        font-size: 25px;
        margin-bottom: 8px;
    }

    .help-title {
        font-size: 17px;
        font-weight: 600;
        color: #173f35;
        margin-bottom: 5px;
    }

    .help-description {
        font-size: 13px;
        color: #6b7773;
    }

    /* Metrics */
    .metric-card {
        background-color: white;
        border: 1px solid #e3e9e6;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    .metric-label {
        color: #687570;
        font-size: 14px;
    }

    .metric-value {
        color: #173f35;
        font-size: 30px;
        font-weight: 700;
        margin-top: 5px;
    }

    /* Section titles */
    .section-title {
        color: #173f35;
        font-size: 21px;
        font-weight: 650;
        margin-top: 30px;
        margin-bottom: 3px;
    }

    .section-subtitle {
        color: #73807b;
        font-size: 13px;
        margin-bottom: 15px;
    }

    /* AI card */
    .ai-card {
        background-color: #e8f1ed;
        border: 1px solid #cbded6;
        border-radius: 12px;
        padding: 18px;
        margin-top: 25px;
        color: #173f35;
    }

    .ai-title {
        font-size: 17px;
        font-weight: 650;
        margin-bottom: 6px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# DATA
# =========================================================

tickets = get_sample_tickets()
summary = summarize_ticket_queue(tickets)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">How can we help you?</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-subtitle">'
    "Find answers, submit a request, or get help from the right team."
    "</div>",
    unsafe_allow_html=True,
)


# =========================================================
# SEARCH
# =========================================================

st.markdown(
    """
    <div class="help-card">
        <div class="help-icon">🔍</div>
        <div class="help-title">Search the Help Center</div>
        <div class="help-description">
            Search articles, policies, guides, and support resources.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

search = st.text_input(
    "Search",
    placeholder="What can we help you find?",
    label_visibility="collapsed",
)


# =========================================================
# QUICK HELP
# =========================================================

st.markdown(
    '<div class="section-title">Quick Help</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    "Find support by department."
    "</div>",
    unsafe_allow_html=True,
)


departments = [
    (
        "👥",
        "HR",
        "Benefits, payroll, time off, employee questions",
    ),
    (
        "💻",
        "IT",
        "Accounts, devices, software, access",
    ),
    (
        "💳",
        "Accounting",
        "Expenses, invoices, payments",
    ),
    (
        "🏢",
        "Facilities",
        "Office access, equipment, workspace",
    ),
]


cols = st.columns(4)

for col, department in zip(
    cols,
    departments,
    strict=True,
):
    icon, name, description = department

    with col:
        st.markdown(
            f"""
            <div class="help-card">
                <div class="help-icon">{icon}</div>
                <div class="help-title">{name}</div>
                <div class="help-description">
                    {description}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            f"Get {name} help",
            key=f"help_{name}",
            use_container_width=True,
        ):
            st.session_state["department"] = name
            st.switch_page("pages/4_new_request.py")


# =========================================================
# YOUR TICKETS
# =========================================================

st.markdown(
    '<div class="section-title">Your Tickets</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    "Track requests you have submitted."
    "</div>",
    unsafe_allow_html=True,
)


col1, col2, col3 = st.columns(3)


with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Open</div>
            <div class="metric-value">{summary["open"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">In Progress</div>
            <div class="metric-value">{summary["in_progress"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Resolved</div>
            <div class="metric-value">{summary["resolved"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# RECENT TICKETS
# =========================================================

st.markdown(
    '<div class="section-title">Recent Tickets</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    "Your latest support requests."
    "</div>",
    unsafe_allow_html=True,
)

st.dataframe(
    tickets,
    use_container_width=True,
    hide_index=True,
)


# =========================================================
# AI ASSISTANT
# =========================================================

st.markdown(
    """
    <div class="ai-card">
        <div class="ai-title">🤖 Genie AI</div>
        <div>
            Need help figuring out where to start?
            Genie can help you find the right department,
            answer common questions, and create a support request.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
