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
    f"Tell us what you need help with and we'll route "
    f"your request to {department}.",
)

# =========================================================
# REQUEST DETAILS
# =========================================================

section_title(
    "Request Details",
    "Tell us what you need help with so we can get "
    "your request to the right team.",
)

# =========================================================
# SUBJECT
# =========================================================

subject = st.text_input(
    "Request subject *",
    placeholder="Briefly describe what you need help with",
)

# =========================================================
# CATEGORY + PRIORITY
# =========================================================

col1, col2 = st.columns(2)

with col1:
    category = st.selectbox(
        "Category *",
        [
            "Select a category",
            "HR",
            "IT",
            "Accounting",
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

# =========================================================
# DESCRIPTION
# =========================================================

description = st.text_area(
    "Description *",
    placeholder=(
        "Describe the issue and include any information "
        "that may help us resolve it."
    ),
    height=180,
)

# =========================================================
# PREFERRED DATE
# =========================================================

preferred_date = st.date_input(
    "Preferred resolution date",
)

# =========================================================
# ATTACHMENTS
# =========================================================

st.markdown("**Supporting files**")

attachment = st.file_uploader(
    "Attach screenshots, documents, or other files",
    accept_multiple_files=True,
)

# =========================================================
# AI PREVIEW
# =========================================================

section_title(
    "Before you submit",
    "Here's what Genie AI will do with your request.",
)

st.markdown(
    """
    <div class="ai-card">
        <div class="ai-title">
            🤖 Genie AI will review this request
        </div>
        <div class="ai-text">
            After submission, Genie AI can identify the request
            type, estimate its priority, route it to the correct
            department, and determine whether it can be resolved
            automatically.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# SUBMIT
# =========================================================

st.markdown("")

if st.button(
    "Submit Request",
    type="primary",
    use_container_width=True,
):

    # -----------------------------------------------------
    # FRONTEND VALIDATION
    # -----------------------------------------------------

    if not subject.strip():
        st.warning("Please enter a request subject.")

    elif not description.strip():
        st.warning("Please describe your issue.")

    elif category == "Select a category":
        st.warning("Please select a category.")

    elif priority == "Select priority":
        st.warning("Please select a priority.")

    else:

        # -------------------------------------------------
        # BACKEND CONNECTION GOES HERE LATER
        # -------------------------------------------------

        # Example for your teammates:
        #
        # ticket_service.create_ticket(
        #     subject=subject,
        #     description=description,
        #     category=category,
        #     priority=priority,
        #     preferred_date=preferred_date,
        #     attachments=attachment,
        # )

        st.success(
            "Your request has been submitted successfully!"
        )

        st.info(
            f"Your request has been sent to the "
            f"{category} support team."
        )
