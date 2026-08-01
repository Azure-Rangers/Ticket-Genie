from __future__ import annotations

from datetime import datetime

import streamlit as st

from app.components.summary_cards import render_summary_cards
from app.services.tickets import get_sample_tickets, summarize_ticket_queue


def build_app_summary() -> dict[str, int | str]:
    tickets = get_sample_tickets()
    queue_summary = summarize_ticket_queue(tickets)

    return {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        **queue_summary,
    }


def main() -> None:
    st.set_page_config(page_title="Ticket-Genie", page_icon="🎫", layout="wide")

    st.title("Ticket-Genie")
    st.write("Streamlit starter app for tracking support tickets and workflow health.")

    summary = build_app_summary()
    render_summary_cards(summary)

    st.subheader("Sample tickets")
    st.dataframe(get_sample_tickets(), use_container_width=True)

    st.caption(f"Snapshot generated {summary['generated_at']}")


if __name__ == "__main__":
    main()