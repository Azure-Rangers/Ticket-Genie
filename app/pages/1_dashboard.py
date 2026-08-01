from __future__ import annotations

import streamlit as st

from app.services.tickets import get_sample_tickets, summarize_ticket_queue

st.set_page_config(page_title="Dashboard | Ticket-Genie", layout="wide")

st.title("Dashboard")
st.write("A quick view into the current support queue.")

tickets = get_sample_tickets()
summary = summarize_ticket_queue(tickets)

columns = st.columns(3)
columns[0].metric("Open", summary["open"])
columns[1].metric("In progress", summary["in_progress"])
columns[2].metric("Resolved", summary["resolved"])

st.dataframe(tickets, use_container_width=True)