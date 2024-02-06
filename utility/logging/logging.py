import logging
from logging.handlers import RotatingFileHandler
import os

plugin_logger = logging.getLogger("perry")
plugin_logger.setLevel(logging.DEBUG)


def get_logger():
    return plugin_logger


def setup_logger_for_emulation(experiment_output_dir: str):
    # join paths
    log_filename = f"perry_log.log"
    log_path = os.path.join(experiment_output_dir, log_filename)

    plugin_logger_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024)
    plugin_logger_formatter = logging.Formatter(
        "%(asctime)s {%(filename)s:%(lineno)d} %(levelname)s:%(message)s"
    )
    plugin_logger_handler.setFormatter(plugin_logger_formatter)
    plugin_logger_handler.setLevel(logging.DEBUG)

    plugin_logger.handlers.clear()
    plugin_logger.addHandler(plugin_logger_handler)


def log(message: str):
    plugin_logger.debug(message)


def log_event(event: str, message: str):
    plugin_logger.debug(f"{event:<24}\t{message}")


def log_trusted_agents(trusted_agents):
    for agent in trusted_agents:
        log_event(
            "TRUSTED AGENT",
            f"{agent.paw} ({agent.host} - {agent.host_ip_addrs})",
        )
