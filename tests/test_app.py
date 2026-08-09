from app.main import (
    build_app_summary,
    render_employee_view,
    render_landing_view,
    render_ticketer_view,
)


def test_build_app_summary_includes_queue_counts() -> None:
    summary = build_app_summary()

    assert summary["open"] == 1
    assert summary["in_progress"] == 1
    assert summary["resolved"] == 1
    assert "generated_at" in summary


def test_view_functions_callable() -> None:
    assert callable(render_landing_view)
    assert callable(render_employee_view)
    assert callable(render_ticketer_view)

