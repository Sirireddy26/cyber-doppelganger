"""
Cyber Doppelgänger - Desktop Agent Logging Module
Provides structured and standardized logging across all agent components.
"""

import logging
import sys
from agent.configuration.config import settings

def setup_logger(name: str = "agent") -> logging.Logger:
    """Configures and returns a standardized logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(log_level)
    return logger

logger = setup_logger("cyber-doppelganger.agent")
