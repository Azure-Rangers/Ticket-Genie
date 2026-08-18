"""
Structural checks on the chatbot <-> current New Request UI integration.

frontend/employee_NM/new-request.html was redesigned with new form IDs
(standardTicketForm/standardSubject/standardDepartment/standardDescription,
leaveTicketForm/leaveTypeSelect/leaveStartDate/leaveEndDate/leaveDescription,
anonymousTicketForm/anonymousCategory/anonymousDescription) and its own
switchTab()/submitEmployeeStandardTicket() etc., while frontend/js/
script.js's chatbot integration used to target an older set of form IDs
(newTicketForm/ticketSubject/anonTicketForm/standardRequestTab/...) that
no longer exist on the page. These tests guard that the chatbot now
targets the CURRENT DOM, still talks to the real backend chatbot
endpoint, still never auto-submits, and that the Leave/Anonymous hard
rules (department_override, is_anonymous) are wired into the current
forms' own submit handlers (which now live inline in new-request.html,
not in script.js).

There's no JS test runner in this repo, so these are content-level
assertions on the actual served files.
"""

from pathlib import Path

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
SCRIPT_JS = (FRONTEND_DIR / "js" / "script.js").read_text()
NEW_REQUEST_HTML = (FRONTEND_DIR / "employee_NM" / "new-request.html").read_text()

OLD_STALE_IDS = (
    "newTicketForm",
    "ticketSubject",
    "ticketCategory",
    "anonTicketForm",
    "anonTicketSubject",
    "anonTicketCategory",
    "anonTicketDescription",
    "standardRequestTab",
    "anonymousRequestTab",
    "leaveRequestTab",
)


def test_genie_widget_calls_the_real_chatbot_endpoint():
    assert "/chatbot/message" in SCRIPT_JS


def test_genie_widget_no_longer_uses_the_legacy_genie_chat_endpoint():
    assert "/genie/chat" not in SCRIPT_JS


def test_no_local_static_genie_response_generator_remains():
    assert "getGenieResponse" not in SCRIPT_JS
    assert "apiGenieChat" not in SCRIPT_JS


def test_conversation_state_fields_are_sent_to_the_backend():
    for field in ("history", "draft", "active_intent", "active_request_type"):
        assert field in SCRIPT_JS


def test_form_opening_is_gated_on_ready_for_review():
    assert "ready_for_review" in SCRIPT_JS


def test_old_ui_ids_are_no_longer_required_by_the_chatbot():
    for stale_id in OLD_STALE_IDS:
        assert stale_id not in SCRIPT_JS, f"stale ID {stale_id!r} still referenced"


def test_prefill_targets_current_standard_form_fields():
    for current_id in ("standardSubject", "standardDescription", "standardDepartment"):
        assert current_id in SCRIPT_JS


def test_prefill_targets_current_leave_form_fields():
    for current_id in ("leaveTypeSelect", "leaveStartDate", "leaveDescription"):
        assert current_id in SCRIPT_JS


def test_prefill_targets_current_anonymous_form_fields():
    assert "anonymousDescription" in SCRIPT_JS


def test_all_three_request_types_map_to_the_current_switchTab_names():
    assert "GENIE_REQUEST_TYPE_TAB_NAMES" in SCRIPT_JS
    assert '"standard"' in SCRIPT_JS
    assert '"leave"' in SCRIPT_JS
    assert '"anonymous"' in SCRIPT_JS
    assert "window.switchTab" in SCRIPT_JS


def test_ready_draft_detection_uses_current_standard_form_id():
    assert 'getElementById("standardTicketForm")' in SCRIPT_JS
    assert 'getElementById("newTicketForm")' not in SCRIPT_JS


def test_chat_response_handling_never_calls_apiCreateTicket():
    # apiCreateTicket is only ever called from the current New Request
    # page's own submit handlers (user clicks the real submit button) -
    # never from the chatbot response-handling functions.
    handler_names = (
        "advanceGenieState",
        "openReadyDraft",
        "prefillRequestForm",
        "handleGenieAction",
        "apiChatbotMessage",
    )
    start = min(SCRIPT_JS.index(f"function {name}") for name in handler_names)
    end = SCRIPT_JS.index("// Bind all global utilities to window")
    assert end > start
    chat_handling_region = SCRIPT_JS[start:end]
    assert "apiCreateTicket(" not in chat_handling_region
    assert ".submit()" not in chat_handling_region
    assert "requestSubmitButton.click" not in chat_handling_region


# ---------------------------------------------------------------------------
# The current New Request page (submission logic now lives inline there,
# consistent with how submitEmployeeStandardTicket already worked)
# ---------------------------------------------------------------------------


def test_standard_form_has_stable_ids_and_submit_handler():
    for current_id in (
        "standardTicketForm",
        "standardSubject",
        "standardDepartment",
        "standardDescription",
        "submitStandardBtn",
    ):
        assert f'id="{current_id}"' in NEW_REQUEST_HTML
    assert "submitEmployeeStandardTicket" in NEW_REQUEST_HTML


def test_leave_form_has_stable_ids_and_submit_handler():
    for current_id in (
        "leaveTicketForm",
        "leaveTypeSelect",
        "leaveHandoverLead",
        "leaveStartDate",
        "leaveEndDate",
        "leaveDescription",
        "leaveFileUpload",
        "submitLeaveBtn",
    ):
        assert f'id="{current_id}"' in NEW_REQUEST_HTML
    assert "submitEmployeeLeaveTicket" in NEW_REQUEST_HTML


def test_anonymous_form_has_stable_ids_and_submit_handler():
    for current_id in (
        "anonymousTicketForm",
        "anonymousCategory",
        "anonymousDescription",
        "anonymousFileUpload",
        "submitAnonymousBtn",
    ):
        assert f'id="{current_id}"' in NEW_REQUEST_HTML
    assert "submitEmployeeAnonymousTicket" in NEW_REQUEST_HTML


def test_leave_submission_sends_deterministic_department_override():
    assert "department_override: 'Upper Management'" in NEW_REQUEST_HTML


def test_anonymous_submission_sets_is_anonymous_true():
    assert "is_anonymous: true" in NEW_REQUEST_HTML


def test_standard_submission_preserves_auto_ai_classification_default():
    assert 'value="Auto"' in NEW_REQUEST_HTML
    assert "Auto (AI Classification)" in NEW_REQUEST_HTML


def test_all_three_forms_only_submit_on_explicit_user_submit_event():
    assert "submitEmployeeStandardTicket(event)" in NEW_REQUEST_HTML
    assert "submitEmployeeLeaveTicket(event)" in NEW_REQUEST_HTML
    assert "submitEmployeeAnonymousTicket(event)" in NEW_REQUEST_HTML


def test_current_tab_switch_mechanism_is_reused_not_duplicated():
    assert "function switchTab(tabType)" in NEW_REQUEST_HTML
    # script.js must not define a second, competing tab-switch mechanism.
    assert "function switchTab(" not in SCRIPT_JS
    assert "function switchRequestTab(" not in SCRIPT_JS
