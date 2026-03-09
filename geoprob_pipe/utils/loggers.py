from __future__ import annotations
import os
import logging
import sqlite3
from datetime import datetime
from logging import Handler
from typing import TYPE_CHECKING
from geoprob_pipe.cmd_app.utils.misc import get_geoprob_pipe_version_number
if TYPE_CHECKING:
    from geoprob_pipe.cmd_app.cmd import ApplicationSettings
    from logging import LogRecord


class SQLiteHandler(Handler):

    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path
        self.app_version = get_geoprob_pipe_version_number()
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                created TIMESTAMP,
                level TEXT,
                message TEXT,
                version TEXT,
                module TEXT,
                function TEXT,
                lineno INTEGER
            )
        """)
        self.conn.commit()

    def emit(self, record: LogRecord):
        created_dt = datetime.fromtimestamp(record.created).isoformat()
        username = os.getenv("USERNAME")
        self.conn.execute(
            "INSERT INTO logs (username, created, level, message, version, module, function, lineno) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                username, created_dt, record.levelname, record.getMessage(),
                self.app_version, record.module, record.funcName, record.lineno
            ))
        self.conn.commit()


class ColorFormatter(logging.Formatter):

    COLORS = {
        logging.DEBUG: "\033[34m",     # blauw
        logging.INFO: "\033[32m",      # groen
        logging.WARNING: "\033[33m",   # geel
        logging.ERROR: "\033[31m",     # rood
        logging.CRITICAL: "\033[1;31m" # bold rood
    }

    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"



def setup_base_logging():
    """ Configure logging for the entire application at INFO-level. Call this once at application startup. Later on,
    when it is clear where the geopackage resides, a handler will be added that logs to the geopackage. """


    logger = logging.getLogger("geoprob-pipe")
    logger.setLevel(logging.DEBUG) # Capture DEBUG, but handlers filter output.

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = ColorFormatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)

    logger.propagate = False


def enable_geopackage_logging(app_settings: ApplicationSettings):
    """ enable logging into the geopackage. Logging level is INFO, unless GeoProb-Pipe is run with the `debug`-flag,
    then level is DEBUG. """

    logger = logging.getLogger("geoprob-pipe")

    level = logging.INFO
    if app_settings.debug:
        level = logging.DEBUG

    sqlite_handler = SQLiteHandler(db_path=app_settings.geopackage_filepath)
    sqlite_handler.setLevel(level)

    logger.addHandler(sqlite_handler)

    logger.info("Logging into GeoProb-Pipe-file now active.")
    logger.debug("Test debug log message.")
