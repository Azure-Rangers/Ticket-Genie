from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Settings | Ticket-Genie", layout="wide")

st.title("Settings")
st.write(
	"Configure ticketing defaults, routing preferences, and deployment options here."
)

st.checkbox("Enable auto-triage", value=True)
st.checkbox("Send Slack notifications", value=False)
st.checkbox("Require approval before closing tickets", value=True)