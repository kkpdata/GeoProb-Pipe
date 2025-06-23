import logging
import os
from colorlog import ColoredFormatter


def initiate_app_logger(repo_root: str):

    # Initiate logger
    logger = logging.getLogger("geoprob_pipe_logger")
    logger.setLevel(logging.INFO)

    # File handler
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler = logging.FileHandler(os.path.join(repo_root, "geoprob_pipe.log"))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        log_colors={
            "INFO": "green",
        }
    )
    # TODO: Time is currently including microseconds. This is too precise for the console. Strip this.
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)