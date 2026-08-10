from __future__ import annotations

import streamlit as st

from app.components.ui import (
    apply_styles,
    page_header,
    section_title,
)

from app.services.tickets import (
    get_sample_tickets,
    summarize_ticket_queue,
)


st.set_page_config(
    page_title="Help & Support | Ticket-Genie",
    page_icon="🎫",
    layout="wide",
)


apply_styles()


# =========================================================
# DATA
# =========================================================

tickets = get_sample_tickets()
summary = summarize_ticket_queue(tickets)


# =========================================================
# HEADER
# =========================================================

page_header(
    "How can we help you?",
    "Find answers, submit a request, or get help from the right team.",
)


# =========================================================
# SEARCH
# =========================================================

st.markdown(
    """
    <div class="card">
        <div class="card-title">
            🔍 Search the Help Center
        </div>
        <div class="card-description">
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

section_title(
    "Quick Help",
    "Find support by department.",
)

departments = [
    ("👥", "HR", "Benefits, payroll, time off, employee questions"),
    ("💻", "IT", "Accounts, devices, software, access"),
    ("💳", "Accounting", "Expenses, invoices, payments"),
    ("🏢", "Facilities", "Office access, equipment, workspace"),
]

cols = st.columns(4)

for col, department in zip(cols, departments):

    icon, name, description = department

    with col:

        st.markdown(
            f"""
            <div class="quick-card">
                <div class="quick-icon">{icon}</div>
                <div class="quick-title">{name}</div>
                <div class="quick-description">
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

section_title(
    "Your Tickets",
    "Track requests you have submitted.",
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


st.write("")

if st.button(
    "View My Tickets →",
    type="primary",
):
    st.switch_page("pages/5_my_tickets.py")


# =========================================================
# RECENT TICKETS
# =========================================================

section_title(
    "Recent Tickets",
    "Your latest support requests.",
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
        <div class="ai-title">
            🤖 Genie AI
        </div>
        <div>
            Need help figuring out where to start?
            Genie can help you find the right department,
            answer common questions, and create a support request.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
