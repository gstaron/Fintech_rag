import json

from fintech_agent.mcp_server import request_human_review, roi_calculator


def test_roi_calculator_computes_expected_savings():
    result = roi_calculator(
        tickets_per_month=1000,
        current_cost_per_ticket_eur=4.0,
        ai_cost_per_ticket_eur=1.0,
        automation_rate=0.5,
    )
    assert "500" in result  # automated tickets
    assert "1500.00 EUR" in result  # monthly savings: 500 * 3.0


def test_request_human_review_never_takes_the_action_itself(monkeypatch, tmp_path):
    import fintech_agent.mcp_server as server_module

    queue_path = tmp_path / "queue.jsonl"
    monkeypatch.setattr(server_module, "REVIEW_QUEUE_PATH", queue_path)

    result = request_human_review(reason="zmena limitu", payload="client=42")

    assert "NEBOLA" in result
    assert "vykonana automaticky" in result
    entries = [json.loads(line) for line in queue_path.read_text(encoding="utf-8").splitlines()]
    assert entries == [{"reason": "zmena limitu", "payload": "client=42"}]
