# import logging
# from colorlog import ColoredFormatter
from datetime import datetime
from geoprob_pipe.utils.validation_messages import BColors

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
    def info(msg: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(BColors.OKGREEN, f"{timestamp} - INFO - {msg}", BColors.ENDC)

    @staticmethod
    def error(msg: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(BColors.FAIL, f"{timestamp} - ERROR - {msg}", BColors.ENDC)

    @staticmethod
    def debug(msg: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(BColors.OKBLUE, f"{timestamp} - DEBUG - {msg}", BColors.ENDC)
