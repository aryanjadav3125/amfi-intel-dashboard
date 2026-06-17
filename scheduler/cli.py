import asyncio
import click
from pipeline.orchestrator import PipelineOrchestrator
from pipeline.risk_engine import RiskEngine
from config.logging_config import get_logger

logger = get_logger("scheduler.cli")

@click.group()
def cli():
    """AMFI mutual fund platform automation CLI dashboard."""
    pass


@cli.command()
def run_now():
    """Triggers the daily AMFI NAV scraping & ingestion pipeline immediately."""
    logger.info("CLI Trigger: Running daily ingestion pipeline immediately...")
    orchestrator = PipelineOrchestrator()
    risk_engine = RiskEngine()
    try:
        inserted = asyncio.run(orchestrator.run_daily_pipeline())
        click.echo(click.style(f"SUCCESS: Ingestion completed. Inserted {inserted} NAV records.", fg="green"))
        
        click.echo("Triggering dynamic risk engine analytics calculation...")
        updated = asyncio.run(risk_engine.update_all_scheme_analytics())
        click.echo(click.style(f"SUCCESS: Dynamic analytics updated for {updated} schemes.", fg="green"))
    except Exception as e:
        click.echo(click.style(f"FAILED: Pipeline run encountered error: {e}", fg="red"), err=True)


@cli.command()
@click.option("--years", default=3, help="Number of historical years of NAV data to simulate backfill")
def run_backfill(years):
    """Generates 3 years of daily benchmark NAV histories to seed the system."""
    logger.info(f"CLI Trigger: Seeding database and running backfill for {years} years...")
    orchestrator = PipelineOrchestrator()
    risk_engine = RiskEngine()
    try:
        inserted = asyncio.run(orchestrator.run_backfill_pipeline(years))
        click.echo(click.style(f"SUCCESS: Backfill completed. Inserted {inserted} historical NAV records.", fg="green"))
        
        click.echo("Triggering dynamic risk engine analytics calculation...")
        updated = asyncio.run(risk_engine.update_all_scheme_analytics())
        click.echo(click.style(f"SUCCESS: Dynamic analytics updated for {updated} schemes.", fg="green"))
    except Exception as e:
        click.echo(click.style(f"FAILED: Historical backfill encountered error: {e}", fg="red"), err=True)


@cli.command()
def run_analytics():
    """Triggers the dynamic financial risk analytics engine to recompute CAGRs and Info Ratios."""
    logger.info("CLI Trigger: Running dynamic risk engine calculations...")
    risk_engine = RiskEngine()
    try:
        updated = asyncio.run(risk_engine.update_all_scheme_analytics())
        click.echo(click.style(f"SUCCESS: Risk engine calculations completed. Updated {updated} schemes.", fg="green"))
    except Exception as e:
        click.echo(click.style(f"FAILED: Risk engine calculations encountered error: {e}", fg="red"), err=True)


if __name__ == "__main__":
    cli()

