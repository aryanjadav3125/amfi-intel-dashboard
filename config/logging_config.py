import sys
from loguru import logger
from config.settings import settings

def configure_logger():
    # Remove default handler
    logger.remove()
    
    # Add standardized stdout handler
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:7}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        enqueue=True,
    )
    
    # Add log file logging
    logger.add(
        "logs/amfi_platform.log",
        rotation="10 MB",
        retention="30 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:7} | {name}:{function}:{line} - {message}",
        enqueue=True,
    )

# Run logger configuration immediately on import
configure_logger()

def get_logger(name: str):
    """
    Returns a structured logger with contextual module name.
    """
    return logger.bind(module_name=name)
