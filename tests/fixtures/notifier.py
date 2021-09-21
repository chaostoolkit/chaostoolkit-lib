from typing import Any

from logzero import logger

__all__ = ["notify"]


def notify(settings: Any, event_payload: Any) -> None:
    logger.debug("boom")


def notify_other(settings: Any, event_payload: Any) -> None:
    logger.debug("doh")
