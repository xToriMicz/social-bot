"""Utility functions — timing, randomization, logging."""

import logging
from random import uniform
from time import sleep

logger = logging.getLogger("social-bot")

# Global speed multiplier (set from config)
_speed_multiplier = 1.0
MIN_SLEEP = 0.3


def set_speed_multiplier(multiplier: float):
    global _speed_multiplier
    _speed_multiplier = max(multiplier, 0.5)


def random_sleep(min_sec: float = 0.5, max_sec: float = 3.0, modulable: bool = True):
    """Sleep for a random duration with human-like variance."""
    delay = uniform(min_sec, max_sec)
    if modulable and _speed_multiplier != 1.0:
        delay /= _speed_multiplier
    delay = max(delay, MIN_SLEEP)
    logger.debug(f"sleep {delay:.2f}s")
    sleep(delay)


def chance(percentage: int) -> bool:
    """Return True with given percentage chance (0-100)."""
    return uniform(0, 100) < percentage


def setup_logging(level: str = "INFO"):
    """Configure logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
