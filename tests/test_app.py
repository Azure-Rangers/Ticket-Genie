from app.main import build_app_summary


def test_build_app_summary_includes_queue_counts() -> None:
    summary = build_app_summary()

    assert summary["open"] == 1
    assert summary["in_progress"] == 1
    assert summary["resolved"] == 1
    assert "generated_at" in summary