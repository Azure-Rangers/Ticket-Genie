from app.services.tickets import get_sample_tickets, summarize_ticket_queue


def test_get_sample_tickets_returns_expected_shape() -> None:
    tickets = get_sample_tickets()

    assert len(tickets) == 3
    assert tickets[0]["id"] == "TCK-1001"


def test_summarize_ticket_queue_counts_statuses() -> None:
    summary = summarize_ticket_queue(get_sample_tickets())

    assert summary == {"open": 1, "in_progress": 1, "resolved": 1}