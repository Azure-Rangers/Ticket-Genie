from __future__ import annotations

import streamlit as st

from app.components.ui import (
    apply_styles,
    page_header,
    section_title,
)

from app.services.tickets import get_sample_tickets


st.set_page_config(
    page_title="My Tickets | Ticket-Genie",
    page_icon="🎫",
    layout="wide",
)


apply_styles()


page_header(
    "My Tickets",
    "View and track your submitted support requests.",
)


tickets = get_sample_tickets()


# =========================================================
# FILTERS
# =========================================================

col1, col2 = st.columns(2)


with col1:

    status = st.selectbox(
        "Status",
        [
            "All",
            "Open",
            "In Progress",
            "Resolved",
        ],
    )


with col2:

    search = st.text_input(
        "Search tickets",
        placeholder="Search by ticket or subject...",
    )


# =========================================================
# TICKETS
# =========================================================

section_title("Your Requests")


filtered = tickets.copy()


if "status" in filtered.columns:

    if status != "All":

        filtered = filtered[
            filtered["status"] == status
        ]


if search:

    search_lower = search.lower()

    filtered = filtered[
        filtered.apply(
            lambda row:
                search_lower
                in " ".join(
                    str(value)
                    for value in row.values
                ).lower(),
            axis=1,
        )
    ]


st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True,
)


# =========================================================
# AI HELP
# =========================================================

st.markdown(
    """
    <div class="ai-card">
        <div class="ai-title">
            🤖 Need help with a ticket?
        </div>

        Genie AI can explain your ticket status
        or help you understand the next steps.
    </div>
    """,
    unsafe_allow_html=True,
)
