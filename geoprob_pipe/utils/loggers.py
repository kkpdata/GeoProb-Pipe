from datetime import datetime
from geoprob_pipe.utils.validation_messages import BColors


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
