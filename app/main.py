from __future__ import annotations

from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from app.components.summary_cards import render_summary_cards
from app.services.tickets import get_sample_tickets, summarize_ticket_queue

# Load environment variables from local .env file
load_dotenv()


def build_app_summary() -> dict[str, int | str]:
    tickets = get_sample_tickets()
    queue_summary = summarize_ticket_queue(tickets)

    return {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        **queue_summary,
    }


def render_landing_view() -> None:
    st.title("Ticket-Genie")
    st.subheader("Select View")
    st.write("Choose a role to access the corresponding workspace.")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Ticketer view", use_container_width=True, type="primary"):
            st.session_state["active_view"] = "ticketer"
            st.rerun()

    with col2:
        if st.button("Employee View", use_container_width=True):
            st.session_state["active_view"] = "employee"
            st.rerun()

    with col3:
        if st.button("Admin View", use_container_width=True):
            # Admin View is unresponsive for now
            pass


def render_employee_view() -> None:
    top_col1, top_col2 = st.columns([5, 1])
    with top_col1:
        st.header("Employee View")
    with top_col2:
        if st.button("⬅ Switch View", key="back_from_employee"):
            st.session_state["active_view"] = "landing"
            st.rerun()


def render_ticketer_view() -> None:
    top_col1, top_col2 = st.columns([5, 1])
    with top_col1:
        st.title("Ticket-Genie")
    with top_col2:
        if st.button("⬅ Switch View", key="back_from_ticketer"):
            st.session_state["active_view"] = "landing"
            st.rerun()

    st.write("Streamlit starter app for tracking support tickets and workflow health.")

    summary = build_app_summary()
    render_summary_cards(summary)

    st.subheader("Sample tickets")
    st.dataframe(get_sample_tickets(), use_container_width=True)

    st.caption(f"Snapshot generated {summary['generated_at']}")


def main() -> None:
    st.set_page_config(page_title="Ticket-Genie", page_icon="🎫", layout="wide")

    if "active_view" not in st.session_state:
        st.session_state["active_view"] = "landing"

    active_view = st.session_state["active_view"]

    if active_view != "ticketer":
        st.markdown(
            """
            <style>
                [data-testid="stSidebar"] {
                    display: none;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

    if active_view == "ticketer":
        render_ticketer_view()
    elif active_view == "employee":
        render_employee_view()
    else:
        render_landing_view()


if __name__ == "__main__":
    main()
