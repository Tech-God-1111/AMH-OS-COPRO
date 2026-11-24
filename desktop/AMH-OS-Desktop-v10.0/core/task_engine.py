"""Hardware-independent task contracts for the future AAPS scheduler."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import uuid

VALID_TARGETS = {"auto", "s3", "wroom", "uno-1", "uno-2"}
UNO_PAYLOAD_LIMIT = 256  # conservative JSON budget for the Uno's 2 KB SRAM


@dataclass(frozen=True)
class TaskRequest:
    task_id: str
    operation: str
    payload: dict
    target: str = "auto"
    priority: int = 5
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def create(cls, operation: str, payload: dict, target: str = "auto", priority: int = 5):
        task = cls(str(uuid.uuid4()), operation, payload, target, priority)
        task.validate()
        return task

    def validate(self) -> None:
        if not isinstance(self.task_id, str) or not self.task_id or len(self.task_id) > 64:
            raise ValueError("task_id must contain 1–64 characters")
        if not isinstance(self.operation, str) or not self.operation.strip() or len(self.operation) > 48:
            raise ValueError("operation must contain 1–48 non-empty characters")
        if not isinstance(self.payload, dict):
            raise ValueError("payload must be a JSON object")
        if not isinstance(self.target, str) or self.target not in VALID_TARGETS:
            raise ValueError(f"target must be one of: {', '.join(sorted(VALID_TARGETS))}")
        if type(self.priority) is not int or not 0 <= self.priority <= 9:
            raise ValueError("priority must be an integer from 0 to 9")
        try:
            encoded = json.dumps(self.payload, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
        except (TypeError, ValueError, RecursionError) as exc:
            raise ValueError("payload must contain finite JSON-compatible values") from exc
        if self.target.startswith("uno-") and len(encoded) > UNO_PAYLOAD_LIMIT:
            raise ValueError(f"Uno payload exceeds the {UNO_PAYLOAD_LIMIT}-byte safety budget")

    def to_dict(self) -> dict:
        self.validate()
        return {
            "task_id": self.task_id,
            "operation": self.operation,
            "payload": self.payload,
            "target": self.target,
            "priority": self.priority,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class TaskResult:
    task_id: str
    ok: bool
    result: dict = field(default_factory=dict)
    error: str | None = None

    def validate(self) -> None:
        if not isinstance(self.task_id, str) or not self.task_id or len(self.task_id) > 64:
            raise ValueError("result task_id is invalid")
        if type(self.ok) is not bool:
            raise ValueError("result ok must be boolean")
        if not isinstance(self.result, dict):
            raise ValueError("result must be a JSON object")
        try:
            json.dumps(self.result, allow_nan=False)
        except (TypeError, ValueError, RecursionError) as exc:
            raise ValueError("result must contain finite JSON-compatible values") from exc
        if self.error is not None and not isinstance(self.error, str):
            raise ValueError("error must be text or None")


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 2
    initial_backoff_ms: int = 250
    max_backoff_ms: int = 2000

    def validate(self) -> None:
        if type(self.max_attempts) is not int or not 1 <= self.max_attempts <= 5:
            raise ValueError("max_attempts must be from 1 to 5")
        if type(self.initial_backoff_ms) is not int or self.initial_backoff_ms < 0:
            raise ValueError("initial_backoff_ms must be non-negative")
        if type(self.max_backoff_ms) is not int or self.max_backoff_ms < self.initial_backoff_ms:
            raise ValueError("max_backoff_ms must be at least initial_backoff_ms")
