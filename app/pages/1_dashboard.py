from __future__ import annotations

import streamlit as st

from app.services.tickets import (
    get_sample_tickets,
    summarize_ticket_queue,
)

st.set_page_config(
    page_title="Analytics Dashboard | Ticket-Genie",
    page_icon="📊",
    layout="wide",
)


# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .subtitle {
        color: #6b7280;
        font-size: 15px;
        margin-bottom: 25px;
    }

    .metric-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
        min-height: 120px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .metric-title {
        color: #6b7280;
        font-size: 14px;
        margin-bottom: 8px;
    }

    .metric-number {
        font-size: 30px;
        font-weight: 700;
        color: #111827;
    }

    .section-title {
        font-size: 21px;
        font-weight: 650;
        margin-top: 25px;
        margin-bottom: 10px;
    }

    .info-card {
        background: #f8fafc;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #e5e7eb;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# DATA
# ---------------------------------------------------------

tickets = get_sample_tickets()
summary = summarize_ticket_queue(tickets)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">HR Analytics Dashboard</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Monitor support requests, ticket activity, and AI resolution.'
    '</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# SUMMARY CARDS
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)


with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Open Tickets</div>
            <div class="metric-number">{summary["open"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">In Progress</div>
            <div class="metric-number">{summary["in_progress"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Resolved</div>
            <div class="metric-number">{summary["resolved"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


total_tickets = (
    summary["open"]
    + summary["in_progress"]
    + summary["resolved"]
)


with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Total Tickets</div>
            <div class="metric-number">{total_tickets}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# TICKET OVERVIEW
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">Ticket Overview</div>',
    unsafe_allow_html=True,
)


left, right = st.columns(2)


with left:

    st.markdown(
        '<div class="info-card">',
        unsafe_allow_html=True,
    )

    st.subheader("Ticket Status")

    st.bar_chart(
        {
            "Tickets": {
                "Open": summary["open"],
                "In Progress": summary["in_progress"],
                "Resolved": summary["resolved"],
            }
        }
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )


with right:

    st.markdown(
        '<div class="info-card">',
        unsafe_allow_html=True,
    )

    st.subheader("Current Queue")

    st.write(
        "Tickets currently being handled by HR or the AI assistant."
    )

    st.metric(
        "Tickets requiring attention",
        summary["open"] + summary["in_progress"],
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# RECENT TICKETS
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">Recent Tickets</div>',
    unsafe_allow_html=True,
)

st.dataframe(
    tickets,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------

st.divider()

if st.button(
    "🎫 Manage Tickets",
    type="primary",
    use_container_width=True,
):
    st.switch_page("pages/2_tickets.py")
