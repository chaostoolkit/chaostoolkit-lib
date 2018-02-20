# -*- coding: utf-8 -*-
from logzero import logger

__all__ = ["notify"]


def notify(settings, event_payload):
    logger.debug("boom")


def notify_other(settings, event_payload):
    logger.debug("doh")
