import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from config.logging_config import get_logger

logger = get_logger("api.middleware")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    HTTP middleware logging request latency and status codes.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        path = request.url.path
        query = request.url.query
        full_path = f"{path}?{query}" if query else path
        
        logger.info(f"--> {request.method} {full_path}")
        
        try:
            response = await call_next(request)
            duration = (time.time() - start_time) * 1000
            logger.info(f"<-- {request.method} {path} | Status: {response.status_code} | Duration: {duration:.2f}ms")
            return response
        except Exception as exc:
            duration = (time.time() - start_time) * 1000
            logger.error(f"!!! CRITICAL FAILURE: {request.method} {path} failed: {exc} | Duration: {duration:.2f}ms")
            # Returns internal server error status
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={"data": None, "meta": None, "error": f"Internal Server Error: {str(exc)}"}
            )
