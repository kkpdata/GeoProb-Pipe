# import logging
# from colorlog import ColoredFormatter
from datetime import datetime


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# def initiate_app_logger(to_console: bool = True):
#
#     # Initiate logger
#     logger = logging.getLogger("geoprob_pipe_logger")
#     logger.setLevel(logging.INFO)
#
#     # Console handler
#     if to_console:
#         console_handler = logging.StreamHandler()
#         console_handler.setLevel(logging.INFO)
#         formatter = ColoredFormatter(
#             "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
#             datefmt= "%Y-%m-%d %H:%M:%S",
#             log_colors={
#                 "INFO": "green",
#             }
#         )
#         console_handler.setFormatter(formatter)
#         logger.addHandler(console_handler)


class TmpAppConsoleHandler:

    @staticmethod
    def info( msg: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(BColors.OKGREEN, f"{timestamp} - INFO - {msg}")
