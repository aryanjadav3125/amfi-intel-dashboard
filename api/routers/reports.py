"""
Reports API Router

Provides endpoints for downloading raw daily/historical NAV text reports directly
from AMFI, as well as generated PDF and Excel analytics spreadsheets for specific funds.
"""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import PlainTextResponse
from scraper.reports_fetcher import ReportsFetcher
from config.logging_config import get_logger
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi.responses import FileResponse
import os
from api.dependencies import get_db
from api.services.report_builder import ReportBuilder

logger = get_logger("api.routers.reports")

router = APIRouter(
    prefix="/reports",
    tags=["Reports Downloads & History Requests"]
)

@router.get("/download")
async def download_raw_report(
    type: str = Query(..., description="Type of report to download: all, open, close, interval")
):
    """
    Streams a daily NAV plain text report (NAVAll.txt, NAVOpen.txt, etc.) directly from AMFI.
    """
    logger.info(f"Received request to download daily raw report: {type}")
    
    if type.lower() not in ["all", "open", "close", "interval"]:
        raise HTTPException(status_code=400, detail="Invalid report type. Supported: all, open, close, interval")
        
    try:
        fetcher = ReportsFetcher()
        content = await fetcher.fetch_nav_report(type)
        
        filename = f"NAV{type.capitalize()}.txt" if type.lower() != "all" else "NAVAll.txt"
        
        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "text/plain"
        }
        
        return PlainTextResponse(content=content, headers=headers)
    except Exception as e:
        logger.error(f"Failed to stream raw report download from AMFI: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to fetch report from AMFI: {str(e)}")


@router.get("/history")
async def download_history_report(
    mf: Optional[str] = Query("", description="Mutual Fund House AMC ID"),
    tp: Optional[str] = Query("", description="Scheme Type ID"),
    from_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Queries historical NAV from portal.amfiindia.com for up to 90 days and returns the plain text report.
    """
    logger.info(f"Received query request for historical NAV: mf={mf}, tp={tp}, from={from_date}, to={to_date}")
    
    if from_date and to_date:
        diff_days = (to_date - from_date).days
        if diff_days > 90:
            raise HTTPException(
                status_code=400, 
                detail="AMFI restricts historical queries to a maximum window of 90 days."
            )
        if diff_days < 0:
            raise HTTPException(
                status_code=400,
                detail="Start date cannot be after end date."
            )
            
    try:
        fetcher = ReportsFetcher()
        content = await fetcher.fetch_nav_history(
            mf_id=mf,
            scheme_type=tp,
            from_date=from_date,
            to_date=to_date
        )
        
        headers = {
            "Content-Disposition": "attachment; filename=NAVHistoryReport.txt",
            "Content-Type": "text/plain"
        }
        
        return PlainTextResponse(content=content, headers=headers)
    except Exception as e:
        logger.error(f"Failed to fetch historical text report from AMFI: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to fetch historical query: {str(e)}")

@router.get("/fund/{fund_id}/pdf")
async def generate_fund_pdf(fund_id: int, db: AsyncSession = Depends(get_db)):
    """
    Generates and downloads a PDF report for a specific mutual fund.
    """
    builder = ReportBuilder(db)
    try:
        filepath = await builder.generate_fund_report(fund_id, "PDF")
        if not os.path.exists(filepath):
            raise HTTPException(status_code=500, detail="Failed to generate report")
        
        return FileResponse(
            path=filepath, 
            filename=os.path.basename(filepath), 
            media_type="application/pdf"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

@router.get("/fund/{fund_id}/excel")
async def generate_fund_excel(fund_id: int, db: AsyncSession = Depends(get_db)):
    """
    Generates and downloads an Excel spreadsheet report for a specific mutual fund.
    """
    builder = ReportBuilder(db)
    try:
        filepath = await builder.generate_fund_report(fund_id, "EXCEL")
        if not os.path.exists(filepath):
            raise HTTPException(status_code=500, detail="Failed to generate report")
        
        return FileResponse(
            path=filepath, 
            filename=os.path.basename(filepath), 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate Excel: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate Excel")
