"""
Structural checks on frontend/js/script.js's chatbot integration.

There's no JS test runner in this repo (no package.json/build tooling),
so these are content-level assertions on the shared script - the same
file every employee_NM page and the legacy top-level pages load. They
guard the specific things this task requires: the widget talks to the
real backend chatbot endpoint (not a local/static responder, not the
older /genie/chat endpoint), state needed for multi-turn continuation is
threaded through, the three forms get opened by request_type (not all
mapped to Standard), and nothing in the chat-response handling path ever
submits a ticket automatically.
"""

from pathlib import Path

SCRIPT_JS = (
    Path(__file__).resolve().parents[1] / "frontend" / "js" / "script.js"
).read_text()


def test_genie_widget_calls_the_real_chatbot_endpoint():
    assert "/chatbot/message" in SCRIPT_JS


def test_genie_widget_no_longer_uses_the_legacy_genie_chat_endpoint():
    assert "/genie/chat" not in SCRIPT_JS


def test_no_local_static_genie_response_generator_remains():
    assert "getGenieResponse" not in SCRIPT_JS


def test_conversation_state_fields_are_sent_to_the_backend():
    for field in ("history", "draft", "active_intent", "active_request_type"):
        assert field in SCRIPT_JS


def test_all_three_request_types_map_to_a_distinct_tab():
    assert '"standard"' in SCRIPT_JS or "standard:" in SCRIPT_JS
    assert "standardRequestTab" in SCRIPT_JS
    assert "anonymousRequestTab" in SCRIPT_JS
    assert "leaveRequestTab" in SCRIPT_JS


def test_form_opening_is_gated_on_ready_for_review():
    assert "ready_for_review" in SCRIPT_JS


def test_chat_response_handling_never_calls_apiCreateTicket():
    # apiCreateTicket is only ever called from the existing form submit
    # handlers (user clicks the real submit button) - never from the
    # chatbot response-handling functions.
    handler_names = (
        "advanceGenieState",
        "openReadyDraft",
        "prefillRequestForm",
        "handleGenieAction",
        "apiChatbotMessage",
    )
    start = min(SCRIPT_JS.index(f"function {name}") for name in handler_names)
    end = SCRIPT_JS.index("function escapeHTML")
    chat_handling_region = SCRIPT_JS[start:end]
    assert "apiCreateTicket(" not in chat_handling_region
    assert ".submit()" not in chat_handling_region
    assert "requestSubmitButton.click" not in chat_handling_region


def test_leave_submission_sends_deterministic_department_override():
    assert "department_override" in SCRIPT_JS
    assert '"Upper Management"' in SCRIPT_JS


def test_anonymous_submission_sets_is_anonymous_true():
    assert 'anonTicketForm: { title: "anonTicketSubject"' in SCRIPT_JS
    assert "anonymous: true" in SCRIPT_JS
