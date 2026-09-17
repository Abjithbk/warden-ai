from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.overview import OverviewStatsOut, RecentActionOut
from backend.services import overview as overview_service

router = APIRouter(prefix="/overview", tags=["overview"])


@router.get("/recent-actions", response_model=list[RecentActionOut])
def get_recent_actions(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    ) -> list[RecentActionOut]:
    return overview_service.get_recent_actions(db, limit=limit)    




@router.get("/stats", response_model=OverviewStatsOut)
def get_overview_stats(db: Session = Depends(get_db)) -> OverviewStatsOut:
    return OverviewStatsOut(
        sentinel_score=overview_service.compute_sentinel_score(db),
        active_incidents=overview_service.count_active_incidents(db),
        auto_resolved_today=overview_service.count_auto_resolved_today(db),
        avg_remediation_seconds=overview_service.compute_avg_remediation_seconds(db),
        actions_last_24h=overview_service.count_actions_last_24h(db),
    )


