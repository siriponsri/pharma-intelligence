"""Loguru-based logging config."""

import sys

from loguru import logger

from pharma_intel.common.config import settings


def setup_logging() -> None:
    """Configure loguru to write formatted logs to stderr."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
    )


# Auto-configure on import
setup_logging()

__all__ = ["logger", "setup_logging"]
