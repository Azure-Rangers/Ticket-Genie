"""Azure Monitor OpenTelemetry Telemetry Setup for FastAPI Backend.

This module handles initializing Azure Application Insights telemetry using the
official Azure Monitor OpenTelemetry Distro (`azure-monitor-opentelemetry`).
"""

import logging
import os
from typing import Optional

from fastapi import FastAPI

logger = logging.getLogger("ticketgenie.telemetry")

_telemetry_initialized = False


def setup_telemetry(
    app: FastAPI, connection_string: Optional[str] = None
) -> bool:
    """Initialize Azure Monitor OpenTelemetry for FastAPI backend.

    Args:
        app: The FastAPI application instance.
        connection_string: Optional explicit connection string. Defaults to
          reading the APPLICATIONINSIGHTS_CONNECTION_STRING environment
          variable.

    Returns:
        bool: True if telemetry was successfully configured, False otherwise.
    """
    global _telemetry_initialized

    if _telemetry_initialized:
        logger.info("Telemetry already initialized.")
        return True

    conn_str = connection_string or os.getenv(
        "APPLICATIONINSIGHTS_CONNECTION_STRING"
    )

    if not conn_str:
        logger.info(
            "APPLICATIONINSIGHTS_CONNECTION_STRING not provided. "
            "Telemetry export to Azure Monitor is disabled."
        )
        return False

    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        # Configure Azure Monitor OpenTelemetry Distro
        configure_azure_monitor(
            connection_string=conn_str,
            logger_name="ticketgenie",
            enable_live_metrics=True,
        )

        # Instrument FastAPI app for route tracing and request metrics
        FastAPIInstrumentor.instrument_app(app)

        _telemetry_initialized = True
        logger.info("Azure Monitor OpenTelemetry telemetry initialized successfully.")
        return True

    except Exception as exc:
        logger.warning(
            f"Failed to initialize Azure Monitor telemetry: {exc}",
            exc_info=True,
        )
        return False
