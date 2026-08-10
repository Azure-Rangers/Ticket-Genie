from __future__ import annotations

import streamlit as st

from app.components.ui import (
    apply_styles,
    page_header,
    section_title,
)


st.set_page_config(
    page_title="New Request | Ticket-Genie",
    page_icon="➕",
    layout="wide",
)


apply_styles()


# =========================================================
# HEADER
# =========================================================

department = st.session_state.get(
    "department",
    "General Support",
)

page_header(
    "Submit a new request",
    f"Tell us what you need help with and we'll route your request to {department}.",
)


# =========================================================
# REQUEST DETAILS
# =========================================================

section_title(
    "Request Details",
    "Provide enough information for our team to understand your issue.",
)


subject = st.text_input(
    "Request subject *",
    placeholder="Briefly describe what you need help with",
)


col1, col2 = st.columns(2)


with col1:

    category = st.selectbox(
        "Category *",
        [
            "Select a category",
            "HR",
            "IT",
            "Accounting",
            "Finance",
            "Facilities",
            "Other",
        ],
    )


with col2:

    priority = st.selectbox(
        "Priority *",
        [
            "Select priority",
            "Low",
            "Medium",
            "High",
        ],
    )


description = st.text_area(
    "Description *",
    placeholder="Describe the issue and include any information that may help us resolve it.",
    height=180,
)


preferred_date = st.date_input(
    "Preferred resolution date",
)


attachment = st.file_uploader(
    "Attach supporting files",
    accept_multiple_files=True,
)


# =========================================================
# AI PREVIEW
# =========================================================

section_title(
    "Before you submit",
)

st.markdown(
    """
    <div class="ai-card">
        <div class="ai-title">
            🤖 Genie AI will review this request
        </div>

        <p>
            After submission, the AI assistant can identify the
            request type, estimate priority, and determine whether
            the request can be automatically resolved.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SUBMIT
# =========================================================

if st.button(
    "Submit Request",
    type="primary",
    use_container_width=True,
):

    if not subject or not description:
        st.warning(
            "Please complete the subject and description."
        )

    elif category == "Select a category":
        st.warning(
            "Please select a category."
        )

    else:

        # =================================================
        # BACKEND CONNECTION GOES HERE LATER
        # =================================================

        # Example:
        #
        # ticket_service.create_ticket(
        #     subject=subject,
        #     description=description,
        #     category=category,
        #     priority=priority,
        # )
        #

        st.success(
            "Your request has been submitted successfully!"
        )

        st.info(
            "Your request has been sent to the appropriate support team."
        )
