import pytest

from core.task_engine import RetryPolicy, TaskRequest, TaskResult


def test_task_request_creation_and_serialization():
    task = TaskRequest.create("sum", {"values": [2, 3]}, target="uno-1", priority=2)
    task.validate()
    assert task.to_dict()["operation"] == "sum"
    assert task.to_dict()["priority"] == 2


def test_task_rejects_unknown_target_and_invalid_priority():
    with pytest.raises(ValueError):
        TaskRequest("id", "sum", {}, target="gpu").validate()
    with pytest.raises(ValueError):
        TaskRequest("id", "sum", {}, priority=10).validate()


def test_uno_payload_budget_is_enforced():
    with pytest.raises(ValueError, match="256-byte"):
        TaskRequest("id", "echo", {"text": "x" * 300}, target="uno-1").validate()


def test_result_contract():
    TaskResult("task-1", True, {"value": 5}).validate()
    with pytest.raises(ValueError):
        TaskResult("task-1", "yes", {}).validate()


def test_retry_policy_bounds():
    RetryPolicy().validate()
    with pytest.raises(ValueError):
        RetryPolicy(max_attempts=8).validate()
