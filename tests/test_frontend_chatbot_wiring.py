"""
Structural checks on the chatbot <-> current employee UI integration.

Employee pages (frontend/employee_NM/*.html) no longer load
frontend/js/script.js as their main script - they now load
frontend/js/employee-script.js (script.js still exists but now serves
other portals, e.g. admin). The chatbot's form-handoff logic
(GENIE_REQUEST_TYPE_TAB_NAMES, prefillRequestForm(), openReadyDraft(),
applyPendingGenieDraft()) needs to live in - and target the current DOM
of - employee-script.js, not script.js.

frontend/employee_NM/new-request.html uses form IDs
(standardTicketForm/standardSubject/standardDepartment/
standardDescription, leaveTicketForm/leaveTypeSelect/leaveStartDate/
leaveEndDate/leaveDescription, anonymousTicketForm/anonymousCategory/
anonymousDescription) and its own switchTab()/submitEmployeeStandardTicket()
etc. An older chatbot integration (whichever file it lived in) targeted a
prior UI revision's IDs (newTicketForm/ticketSubject/anonTicketForm/
standardRequestTab/...) that no longer exist on the page.

There's no JS test runner in this repo, so these are content-level
assertions on the actual served files.
"""

from pathlib import Path

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
EMPLOYEE_SCRIPT_JS = (FRONTEND_DIR / "js" / "employee-script.js").read_text()
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
    ".tab-btn[data-target",
)

# The "old field" spelling of leave type - the CURRENT leave type select
# id is leaveTypeSelect (checked separately); this bare "leaveType" name
# (no "Select" suffix) was the stale pre-current-UI field id.
_OLD_LEAVE_TYPE_FIELD = '"leaveType"'


def test_employee_pages_load_employee_script_not_script_js_for_chatbot():
    employee_pages = [
        FRONTEND_DIR / "employee_NM" / "new-request.html",
        FRONTEND_DIR / "employee_NM" / "index.html",
        FRONTEND_DIR / "employee_NM" / "my-tickets.html",
    ]
    for page_path in employee_pages:
        page = page_path.read_text()
        assert "employee-script.js" in page, (
            f"{page_path.name} must load employee-script.js"
        )


def test_genie_widget_calls_the_real_chatbot_endpoint():
    assert "/chatbot/message" in EMPLOYEE_SCRIPT_JS


def test_genie_widget_no_longer_uses_the_legacy_genie_chat_endpoint():
    assert "/genie/chat" not in EMPLOYEE_SCRIPT_JS


def test_no_local_static_genie_response_generator_remains():
    assert "getGenieResponse" not in EMPLOYEE_SCRIPT_JS
    assert "apiGenieChat" not in EMPLOYEE_SCRIPT_JS


def test_conversation_state_fields_are_sent_to_the_backend():
    assert "GENIE_STATE_KEY" in EMPLOYEE_SCRIPT_JS
    for field in ("history", "draft", "active_intent", "active_request_type"):
        assert field in EMPLOYEE_SCRIPT_JS


def test_form_opening_is_gated_on_ready_for_review():
    assert "ready_for_review" in EMPLOYEE_SCRIPT_JS


def test_old_ui_ids_are_no_longer_required_by_the_chatbot():
    for stale_id in OLD_STALE_IDS:
        assert stale_id not in EMPLOYEE_SCRIPT_JS, (
            f"stale ID {stale_id!r} still referenced"
        )
    assert _OLD_LEAVE_TYPE_FIELD not in EMPLOYEE_SCRIPT_JS


def test_prefill_targets_current_standard_form_fields():
    for current_id in ("standardSubject", "standardDescription", "standardDepartment"):
        assert current_id in EMPLOYEE_SCRIPT_JS


def test_prefill_targets_current_leave_form_fields_including_end_date():
    for current_id in (
        "leaveTypeSelect",
        "leaveStartDate",
        "leaveEndDate",
        "leaveDescription",
    ):
        assert current_id in EMPLOYEE_SCRIPT_JS
    # startDate and endDate must map to their own distinct fields, not one
    # value duplicated into both.
    assert 'setFieldValue("leaveStartDate"' in EMPLOYEE_SCRIPT_JS
    assert 'setFieldValue("leaveEndDate", draft.endDate)' in EMPLOYEE_SCRIPT_JS


def test_prefill_targets_current_anonymous_form_fields():
    assert "anonymousDescription" in EMPLOYEE_SCRIPT_JS


def test_all_three_request_types_map_to_the_current_switchTab_names():
    assert "GENIE_REQUEST_TYPE_TAB_NAMES" in EMPLOYEE_SCRIPT_JS
    assert '"standard"' in EMPLOYEE_SCRIPT_JS
    assert '"leave"' in EMPLOYEE_SCRIPT_JS
    assert '"anonymous"' in EMPLOYEE_SCRIPT_JS
    assert "window.switchTab" in EMPLOYEE_SCRIPT_JS


def test_chatbot_does_not_define_a_second_tab_switch_mechanism():
    assert "function switchTab(" not in EMPLOYEE_SCRIPT_JS
    assert "function switchRequestTab(" not in EMPLOYEE_SCRIPT_JS
    assert "function switchTab(tabType)" in NEW_REQUEST_HTML


def test_ready_draft_detection_uses_current_standard_form_id():
    assert 'getElementById("standardTicketForm")' in EMPLOYEE_SCRIPT_JS
    assert 'getElementById("newTicketForm")' not in EMPLOYEE_SCRIPT_JS


def test_stale_double_form_handler_is_removed():
    # initializeNewRequestForm() used to bind a second, stale submit
    # listener onto the current leaveTicketForm - it must be gone
    # entirely, not just uncalled.
    assert "function initializeNewRequestForm" not in EMPLOYEE_SCRIPT_JS
    assert "formConfigs" not in EMPLOYEE_SCRIPT_JS


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
    start = min(EMPLOYEE_SCRIPT_JS.index(f"function {name}") for name in handler_names)
    end = EMPLOYEE_SCRIPT_JS.index("// Bind all global utilities to window")
    assert end > start
    chat_handling_region = EMPLOYEE_SCRIPT_JS[start:end]
    assert "apiCreateTicket(" not in chat_handling_region
    assert ".submit()" not in chat_handling_region
    assert "requestSubmitButton.click" not in chat_handling_region


# ---------------------------------------------------------------------------
# The current New Request page (submission logic lives inline there,
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


def test_leave_submission_reads_both_dates_and_stays_explicit_submit_only():
    assert "getElementById('leaveStartDate')" in NEW_REQUEST_HTML
    assert "getElementById('leaveEndDate')" in NEW_REQUEST_HTML
    assert (
        'onsubmit="event.preventDefault(); submitEmployeeLeaveTicket(event); return false;"'
        in NEW_REQUEST_HTML
    )


def test_anonymous_submission_sets_is_anonymous_true():
    assert "is_anonymous: true" in NEW_REQUEST_HTML


def test_standard_submission_preserves_auto_ai_classification_default():
    assert 'value="Auto"' in NEW_REQUEST_HTML
    assert "Auto (AI Classification)" in NEW_REQUEST_HTML


def test_all_three_forms_only_submit_on_explicit_user_submit_event():
    assert "submitEmployeeStandardTicket(event)" in NEW_REQUEST_HTML
    assert "submitEmployeeLeaveTicket(event)" in NEW_REQUEST_HTML
    assert "submitEmployeeAnonymousTicket(event)" in NEW_REQUEST_HTML
