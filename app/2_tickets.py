from __future__ import annotations

import streamlit as st

from app.services.tickets import get_sample_tickets

st.set_page_config(
    page_title="Manage Tickets | Ticket-Genie",
    page_icon="🎫",
    layout="wide",
)


# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .page-title {
        font-size: 30px;
        font-weight: 700;
    }

    .subtitle {
        color: #6b7280;
        margin-bottom: 25px;
    }

    .ticket-card {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        background: white;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    '<div class="page-title">Manage Tickets</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Review, prioritize, and resolve employee support requests."
    "</div>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# LOAD TICKETS
# ---------------------------------------------------------

tickets = get_sample_tickets()


# ---------------------------------------------------------
# SEARCH / FILTER
# ---------------------------------------------------------

search = st.text_input(
    "🔎 Search tickets",
    placeholder="Search by employee, subject, or category...",
)


status_filter = st.selectbox(
    "Status",
    [
        "All",
        "Open",
        "In Progress",
        "Resolved",
    ],
)


# ---------------------------------------------------------
# FILTER DATA
# ---------------------------------------------------------

filtered_tickets = tickets.copy()


if search:
    search_lower = search.lower()

    filtered_tickets = filtered_tickets[
        filtered_tickets.apply(
            lambda row: (
                search_lower in " ".join(str(value) for value in row.values).lower()
            ),
            axis=1,
        )
    ]


if status_filter != "All":
    filtered_tickets = filtered_tickets[filtered_tickets["status"] == status_filter]


# ---------------------------------------------------------
# TICKET TABLE
# ---------------------------------------------------------

st.write(f"Showing {len(filtered_tickets)} ticket(s)")


st.dataframe(
    filtered_tickets,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# SELECT TICKET
# ---------------------------------------------------------

st.divider()

st.subheader("Ticket Details")


if len(filtered_tickets) > 0:
    ticket_options = filtered_tickets.index.tolist()

    selected_index = st.selectbox(
        "Select a ticket",
        ticket_options,
        format_func=lambda index: f"Ticket #{index + 1}",
    )

    selected_ticket = filtered_tickets.loc[selected_index]

    st.markdown("### Employee Request")

    st.info(str(selected_ticket.to_dict()))

    # -----------------------------------------------------
    # AI ANALYSIS
    # -----------------------------------------------------

    st.markdown("### 🤖 AI Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Priority",
            "Medium",
        )

    with col2:
        st.metric(
            "Intent",
            "Support Request",
        )

    with col3:
        st.metric(
            "AI Recommendation",
            "Review",
        )

    # -----------------------------------------------------
    # HR RESPONSE
    # -----------------------------------------------------

    st.markdown("### HR Response")

    response = st.text_area(
        "Response to employee",
        placeholder="Type your response here...",
        height=150,
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Send Response",
            type="primary",
            use_container_width=True,
        ):
            if response.strip():
                st.success("Response sent successfully.")

                # Later:
                # POST /api/tickets/{ticket_id}/messages

            else:
                st.warning("Please enter a response.")

    with col2:
        if st.button(
            "✓ Resolve Ticket",
            use_container_width=True,
        ):
            st.success("Ticket marked as resolved.")

            # Later:
            # PATCH /api/tickets/{ticket_id}


else:
    st.info("No tickets match your search.")
