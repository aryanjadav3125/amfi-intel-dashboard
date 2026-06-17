"""
Pipeline API Router

Exposes endpoints to retrieve the status and audit logs of the background
AMFI ingestion pipeline. Used by the dashboard to show real-time synchronization states.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from database.models import PipelineRun
from config.logging_config import get_logger

logger = get_logger("api.routers.pipeline")

router = APIRouter(
    prefix="/pipeline",
    tags=["Pipeline Audit Status"]
)

@router.get("/status")
async def get_pipeline_status(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Retrieves execution results and status of the latest AMFI ingestion run.
    """
    logger.debug("Querying latest pipeline execution status...")
    
    result = await db.execute(
        select(PipelineRun).order_by(PipelineRun.run_id.desc()).limit(1)
    )
    latest_run = result.scalar_one_or_none()
    
    if not latest_run:
        return {
            "run_id": None,
            "run_type": None,
            "status": "idle",
            "started_at": None,
            "completed_at": None,
            "records_inserted": 0,
            "records_skipped": 0,
            "errors_count": 0
        }
        
    return {
        "run_id": latest_run.run_id,
        "run_type": latest_run.run_type,
        "status": latest_run.status,
        "started_at": latest_run.started_at,
        "completed_at": latest_run.completed_at,
        "records_inserted": latest_run.records_inserted,
        "records_skipped": latest_run.records_skipped,
        "errors_count": latest_run.errors_count
    }
