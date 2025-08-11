import logging
import os
from colorlog import ColoredFormatter


def initiate_app_logger(to_console: bool = True):

    # Initiate logger
    logger = logging.getLogger("geoprob_pipe_logger")
    logger.setLevel(logging.INFO)

    # Console handler
    if to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
            datefmt= "%Y-%m-%d %H:%M:%S",
            log_colors={
                "INFO": "green",
            }
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
