from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import PipelineRun
from config.logging_config import get_logger

logger = get_logger("pipeline.audit")

class PipelineAudit:
    """
    Manages auditing and logs of data pipeline execution runs in the database.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def start_run(self, run_type: str) -> PipelineRun:
        """
        Creates a new PipelineRun record at the start of a run.
        """
        run = PipelineRun(
            run_type=run_type,
            started_at=datetime.utcnow(),
            status="started"
        )
        self.session.add(run)
        await self.session.flush()
        logger.info(f"Initialized Pipeline Run {run.run_id} ({run_type}).")
        return run

    async def complete_run(
        self, run: PipelineRun, records_inserted: int, records_skipped: int, errors_count: int, status: str
    ) -> None:
        """
        Updates the execution results at the end of a run.
        """
        run.completed_at = datetime.utcnow()
        run.records_inserted = records_inserted
        run.records_skipped = records_skipped
        run.errors_count = errors_count
        run.status = status
        
        self.session.add(run)
        await self.session.flush()
        logger.info(
            f"Pipeline Run {run.run_id} finished. Status: {status}. "
            f"Inserted: {records_inserted}, Skipped: {records_skipped}, Errors: {errors_count}."
        )
