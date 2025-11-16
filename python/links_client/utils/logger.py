"""Logging utility for links-client"""

import logging
import sys
from typing import Optional


def get_logger(name: str = "links_client", level: Optional[int] = None) -> logging.Logger:
    """
    Get or create a logger instance

    Args:
        name: Logger name
        level: Logging level (defaults to WARNING)

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        if level is None:
            level = logging.WARNING

        logger.setLevel(level)

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger
