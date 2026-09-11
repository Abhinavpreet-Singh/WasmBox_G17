from src.api.routes.security import get_security_stats


class FakeResult:
    def __init__(self, executions):
        self.executions = executions

    def all(self):
        return self.executions


class FakeSession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def scalars(self, _query):
        return FakeResult([])


def test_security_stats_without_database_records(monkeypatch):
    monkeypatch.setattr(
        "src.api.routes.security.SessionLocal",
        lambda: FakeSession(),
    )

    result = get_security_stats()

    assert result == {
        "total_executions": 0,
        "safe_executions": 0,
        "detected_attacks": 0,
        "attack_counts": {},
        "average_duration_ms": 0,
    }