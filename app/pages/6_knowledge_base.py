from __future__ import annotations

import streamlit as st

from app.components.ui import (
    apply_styles,
    page_header,
    section_title,
)


st.set_page_config(
    page_title="Knowledge Base | Ticket-Genie",
    page_icon="📖",
    layout="wide",
)


apply_styles()


page_header(
    "Knowledge Base",
    "Find answers to common workplace questions.",
)


search = st.text_input(
    "Search knowledge base",
    placeholder="Search policies, guides, and FAQs...",
)


section_title(
    "Browse by Department",
)


departments = {
    "👥 HR": [
        "Benefits",
        "Time Off",
        "Payroll",
        "Employee Policies",
    ],
    "💻 IT": [
        "Password Reset",
        "Software Access",
        "Computer Issues",
        "Account Access",
    ],
    "💳 Accounting": [
        "Expenses",
        "Invoices",
        "Payments",
        "Purchasing",
    ],
    "🏢 Facilities": [
        "Office Access",
        "Equipment",
        "Workspace",
        "Maintenance",
    ],
}


for department, topics in departments.items():

    with st.expander(department):

        for topic in topics:

            st.write(
                f"→ {topic}"
            )
