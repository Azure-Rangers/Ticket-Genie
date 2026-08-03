from __future__ import annotations

import streamlit as st


def render_summary_cards(summary: dict[str, int | str]) -> None:
    columns = st.columns(4)
    columns[0].metric("Open", summary["open"])
    columns[1].metric("In progress", summary["in_progress"])
    columns[2].metric("Resolved", summary["resolved"])
    columns[3].metric("Generated", summary["generated_at"])
