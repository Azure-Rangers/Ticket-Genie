from __future__ import annotations

import os
from datetime import datetime

import streamlit as st
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from app.components.summary_cards import render_summary_cards
from app.services.tickets import get_sample_tickets, summarize_ticket_queue


def load_multiple_keyvaults_to_env():
    # Define your vaults
    vault_urls = [
        "https://group-1.vault.azure.net/",
        "https://kv-app-prod-12345.vault.azure.net/",
    ]

    # 1. Instantiate the credential exactly ONCE.
    # This automatically picks up your local Azure CLI credentials.
    credential = DefaultAzureCredential()

    for vault_url in vault_urls:
        print(f"Loading secrets from {vault_url}...")

        # 2. Create a client for this specific vault using the shared credential
        client = SecretClient(vault_url=vault_url, credential=credential)

        # 3. List all secrets in the vault
        secret_properties = client.list_properties_of_secrets()

        for prop in secret_properties:
            # 4. Fetch the actual plaintext value
            secret_value = client.get_secret(prop.name).value

            # 5. Format the key name (e.g., "db-password" -> "DB_PASSWORD")
            env_key = prop.name.replace("-", "_").upper()

            # 6. Inject it into Python's environment variables
            os.environ[env_key] = secret_value


# Now you just read from os.environ, no Azure SDK knowledge required here!
# db_password = os.getenv("DB_PASSWORD")
# api_key = os.getenv("API_KEY")

print("App initialized successfully with secure secrets.")


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
    load_multiple_keyvaults_to_env()

    st.set_page_config(
        page_title="Ticket-Genie",
        page_icon="🎫",
        layout="wide",
    )

    st.title("Ticket-Genie")
    st.write(
        "Streamlit starter app for tracking support tickets and workflow health."
    )

    summary = build_app_summary()
    render_summary_cards(summary)

    st.subheader("Sample tickets")
    st.dataframe(
        get_sample_tickets(),
        use_container_width=True,
    )

    st.caption(
        f"Snapshot generated {summary['generated_at']}"
    )

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
