"""
Structured JSON logging via structlog. Import `logger` anywhere and use it
instead of print() or the stdlib logging module directly.

Example:
    from backend.core.logging import logger
    logger.info("incident_created", incident_id=incident.id, severity="high")
"""

import logging
import sys

import structlog


def configure_logging(environment: str = "local") -> None:
    """Call this once, at app startup."""
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if environment == "local":
        # Pretty, colored output while developing
        renderer = structlog.dev.ConsoleRenderer()
    else:
        # Real JSON lines in staging/production for log aggregation
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)


logger = structlog.get_logger()
