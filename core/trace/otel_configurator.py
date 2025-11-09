"""
Configuration utilities for Azure Monitor and logging instrumentation.

This module sets up Azure Monitor, configures logging, and instruments
urllib3 and Tornado for telemetry collection.
"""

import logging
import logging.config
import os

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.tornado import TornadoInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor

from core.trace.logging_config import LOGGING_CONFIG


class OtelConfigurator:
    """
    Configures Azure Monitor telemetry and logging instrumentation.

    This class sets up Azure Monitor, configures logging, and instruments
    urllib3 and Tornado for telemetry collection.
    """

    _monitor_configured = False
    _logger_configured = False

    @classmethod
    def configure(cls) -> None:
        """
        Set up Azure Monitor telemetry, configure logging, and instrument urllib3 and Tornado.

        This method ensures that Azure Monitor and logging are configured only once,
        and instruments urllib3 and Tornado for telemetry collection if the appropriate
        environment variable is set.
        """
        if not cls._monitor_configured and os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING"):
            configure_azure_monitor()
            logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
            logging.getLogger("azure.identity").setLevel(logging.WARNING)

            URLLib3Instrumentor().instrument()  # identify Azure SDK using urllib3
            TornadoInstrumentor().instrument()  # Streamlit using tornado

            cls._monitor_configured = True

        if not cls._logger_configured:
            logging.config.dictConfig(LOGGING_CONFIG)
            cls._logger_configured = True
