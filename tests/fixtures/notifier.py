from logzero import logger

__all__ = ["notify", "notify_other", "notify_broken"]


def notify(settings, event_payload):
    logger.debug("boom")


def notify_other(settings, event_payload):
    logger.debug("doh")


def notify_broken(settings, event_payload):
    raise Exception("An Exception")
