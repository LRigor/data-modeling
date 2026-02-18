"""
Logging configuration for the application.
"""
import logging
import sys
from typing import Optional
from app.config import settings


def setup_logging(log_level: Optional[str] = None) -> logging.Logger:
    """
    Configure application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                   Defaults to settings.LOG_LEVEL.
    
    Returns:
        Configured logger instance.
    """
    level = log_level or settings.log_level.upper()
    
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("mytomorrows")
    logger.setLevel(getattr(logging, level, logging.INFO))
    
    return logger


logger = setup_logging()
