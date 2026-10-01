from datetime import UTC, datetime

from backend.models.enums import IncidentSeverity, IncidentStatus
from backend.models.incident import Incident


def test_overview_stats_with_resolved_incident(client, db_session):
    db_session.add(
        Incident(
            title="Resolved today",
            service="checkout",
            namespace="prod",
            severity=IncidentSeverity.low,
            status=IncidentStatus.resolved,
            resolved_at=datetime.now(UTC),
        )
    )
    db_session.commit()

    response = client.get("/api/v1/overview/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["auto_resolved_today"] == 1
    assert body["avg_remediation_seconds"] is not None