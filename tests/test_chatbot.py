from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def chat(message, **kwargs):
    payload = {"message": message, **kwargs}
    response = client.post("/api/chatbot/message", json=payload)
    assert response.status_code == 200
    return response.json()


# 1. Dashboard navigation question
def test_dashboard_navigation_does_not_offer_ticket_creation():
    data = chat("How do I access my dashboard?")
    assert data["intent"] == "navigation"
    assert data["action"]["type"] == "navigate"
    assert data["action"]["target"] == "index.html"
    assert data["ticket_draft"] is None
    assert "ticket" not in data["message"].lower()


def test_management_dashboard_navigation_routes_to_management_portal():
    data = chat("How do I access my dashboard?", role="Management")
    assert data["intent"] == "navigation"
    assert data["action"]["target"] == "pages/management-portal.html"


# 2. General how-to question
def test_how_to_reimbursement_question():
    data = chat("Where do I submit a reimbursement?")
    assert data["intent"] in ("navigation", "how_to")
    assert data["action"] is not None
    assert data["action"]["target"] == "new-request.html"
    assert data["ticket_draft"] is None


# 3. Authorized knowledge question
def test_authorized_hr_knowledge_question():
    data = chat(
        "What is the HR escalation procedure for disciplinary cases?",
        role="Employee",
        department="HR",
    )
    assert data["intent"] == "knowledge"
    assert data["knowledge_verified"] is True
    assert "HR" in data["message"] or "escalation" in data["message"].lower()


# 4. Unauthorized department knowledge request
def test_unauthorized_department_knowledge_is_not_exposed():
    data = chat(
        "What is the HR escalation procedure for disciplinary cases?",
        role="Employee",
        department="Accounting",
    )
    assert data["intent"] == "knowledge"
    assert data["knowledge_verified"] is False
    assert "escalation steps" not in data["message"].lower()
    assert "disciplinary" not in data["message"].lower()


def test_general_employee_cannot_see_accounting_internal_data():
    data = chat("What are the vendor payment approval thresholds?", role="Employee")
    assert data["knowledge_verified"] is False


# 5. Support issue starts ticket drafting
def test_support_issue_starts_ticket_drafting():
    data = chat("My laptop won't turn on and I have a deadline tomorrow morning.")
    assert data["intent"] == "support_issue"
    assert data["ticket_draft"] is not None


# 6. Short ticket description with missing information
def test_short_description_asks_follow_up():
    data = chat("My laptop is broken.")
    assert data["intent"] == "support_issue"
    assert "description" in data["missing_fields"]
    assert "?" in data["message"]


# 7. Complete issue description returns filled draft
def test_complete_issue_description_returns_filled_draft():
    data = chat(
        "My laptop crashes whenever I open Teams and I need it fixed before Friday."
    )
    assert data["intent"] == "support_issue"
    assert data["missing_fields"] == []
    draft = data["ticket_draft"]
    assert draft["description"]
    assert draft["title"]
    assert draft["category"] == "IT & Technology"
    assert draft["preferredDate"] is not None


# 8. Ticket draft exactly follows current TicketCreate / Standard Request format
def test_ticket_draft_matches_ticket_create_schema():
    data = chat(
        "My laptop crashes whenever I open Teams and I need it fixed before Friday."
    )
    draft = data["ticket_draft"]
    assert set(draft.keys()) == {
        "title",
        "category",
        "priority",
        "department",
        "description",
        "preferredDate",
        "is_anonymous",
        "attachment",
    }
    assert draft["priority"] is None
    assert draft["department"] is None


# 9. User review is required before submission (drafting never calls ticket creation)
def test_drafting_never_creates_a_real_ticket():
    before = client.get("/api/tickets").json()
    chat("My laptop crashes whenever I open Teams and I need it fixed before Friday.")
    after = client.get("/api/tickets").json()
    assert len(before) == len(after)


# 10. Leave-management request routes to Standard Request draft
def test_leave_management_request_routes_to_draft():
    data = chat(
        "I need medical leave next week starting Monday for a surgery recovery."
    )
    assert data["intent"] == "leave_management"
    assert data["ticket_draft"] is not None
    assert data["ticket_draft"]["category"] == "Medical Leave"


def test_leave_policy_question_is_knowledge_not_drafting():
    data = chat("What is the PTO policy?")
    assert data["intent"] == "knowledge"
    assert data["ticket_draft"] is None


# 11. Incomplete leave request asks required follow-up questions
def test_incomplete_leave_request_asks_follow_up():
    data = chat("I need to request some leave.")
    assert data["intent"] == "leave_management"
    assert data["missing_fields"]
    assert "?" in data["message"]


# 12. Complete leave request creates correctly formatted draft
def test_complete_leave_request_creates_formatted_draft():
    data = chat(
        "I need parental leave starting Monday, my partner is having a baby and I'll "
        "need time to help at home."
    )
    assert data["intent"] == "leave_management"
    assert data["missing_fields"] == []
    draft = data["ticket_draft"]
    assert draft["category"] == "Parental Leave"
    assert draft["preferredDate"] is not None
    assert set(draft.keys()) == {
        "title",
        "category",
        "priority",
        "department",
        "description",
        "preferredDate",
        "is_anonymous",
        "attachment",
    }


# 13. Chatbot does not invent missing information
def test_chatbot_does_not_invent_priority_or_department():
    data = chat(
        "My laptop crashes whenever I open Teams and I need it fixed before Friday."
    )
    draft = data["ticket_draft"]
    assert draft["priority"] is None
    assert draft["department"] is None
    assert draft["attachment"] is None


# 14. Knowledge unavailable - does not hallucinate
def test_unverifiable_knowledge_does_not_hallucinate():
    data = chat("What is the office snack budget for the Mars expansion team?")
    assert data["intent"] == "knowledge"
    assert data["knowledge_verified"] is False
    assert "couldn't verify" in data["message"].lower()


# 15. Existing ticket-status intent
def test_ticket_status_with_id_returns_lookup_action():
    data = chat("Where is ticket HD-1024?")
    assert data["intent"] == "ticket_status"
    assert data["action"]["type"] == "lookup_ticket"
    assert data["action"]["ticket_id"] == "HD-1024"


def test_ticket_status_without_id_navigates_to_my_tickets():
    data = chat("What's the status of my ticket?")
    assert data["intent"] == "ticket_status"
    assert data["action"]["target"] == "my-tickets.html"


# Multi-turn continuation: answering a follow-up should not restart classification
def test_follow_up_answer_continues_leave_draft():
    first = chat("I need to request some leave.")
    assert first["intent"] == "leave_management"

    second = chat(
        "Medical leave, starting next Monday, recovering from a minor surgery.",
        active_intent="leave_management",
        draft=first["ticket_draft"],
    )
    assert second["intent"] == "leave_management"
    assert second["ticket_draft"]["category"] == "Medical Leave"
