import asyncio
from pipeline.orchestrator import PipelineOrchestrator
import notifications
from config.logging_config import get_logger

logger = get_logger("scheduler.jobs")

def run_daily_job() -> None:
    """
    Synchronous wrapper to run daily job.
    Called directly by APScheduler.
    """
    logger.info("Scheduler triggered run_daily_job!")
    try:
        # Create event loop or fetch running loop to execute async task
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    loop.run_until_complete(async_run_daily_job())

async def async_run_daily_job() -> None:
    """
    Asynchronous runner for daily pipeline ingestion job.
    Triggers success/failure notifications appropriately.
    """
    orchestrator = PipelineOrchestrator()
    try:
        logger.info("Executing daily job pipeline...")
        records = await orchestrator.run_daily_pipeline()
        
        summary = (
            f"AMFI Ingestion completed successfully.\n"
            f"Timestamp: {asyncio.get_event_loop().time()}\n"
            f"Successfully processed and upserted: {records} NAV values."
        )
        await notifications.send_success(summary)
        
    except Exception as exc:
        logger.error(f"Daily job pipeline execution encountered critical error: {exc}")
        err_details = (
            f"Pipeline failed critically during scheduled execution.\n"
            f"Exception occurred: {type(exc).__name__}\n"
            f"Error details: {exc}"
        )
        await notifications.send_failure(err_details)
