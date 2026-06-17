import time
import signal
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from config.settings import settings
from config.logging_config import get_logger
from scheduler.jobs import run_daily_job

logger = get_logger("scheduler.main")

def start_scheduler() -> None:
    """
    Spins up the blocking APScheduler daemon to orchestrate automatic daily cron jobs.
    """
    logger.info("Starting AMFI Mutual Fund Data Scheduler service...")
    
    cron_hour = settings.SCHEDULER_CRON_HOUR
    cron_minute = settings.SCHEDULER_CRON_MINUTE
    
    scheduler = BlockingScheduler()
    
    # Configure cron trigger
    trigger = CronTrigger(
        hour=cron_hour,
        minute=cron_minute,
        timezone="Asia/Kolkata"  # Defaulting to IST after AMFI uploads
    )
    
    logger.info(f"Registering daily ingestion cron job. Scheduled to run at {cron_hour:02d}:{cron_minute:02d} IST.")
    
    scheduler.add_job(
        func=run_daily_job,
        trigger=trigger,
        id="daily_amfi_ingestion",
        name="Fetch and update daily mutual fund Net Asset Values from AMFI",
        replace_existing=True
    )
    
    # Signal handlers for clean termination in Docker
    def handle_shutdown(signum, frame):
        logger.info(f"Signal {signum} received. Stopping APScheduler daemon gracefully...")
        scheduler.shutdown(wait=True)
        logger.info("Scheduler service stopped.")
        sys.exit(0)
        
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Manual shutdown triggered.")
        if scheduler.running:
            scheduler.shutdown(wait=False)
            
if __name__ == "__main__":
    start_scheduler()
