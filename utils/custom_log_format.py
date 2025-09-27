import logging
import threading
from logging.handlers import TimedRotatingFileHandler
from os import makedirs

from utils.root import get_project_root

SEM = threading.Semaphore(1)
_shared_file_handlers = {}
class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    # ANSI escape codes for colors
    grey = "\x1b[38;1m"
    bright_green = "\u001b[32;1m"
    yellow = "\x1b[33;1m"
    red = "\u001b[31m"
    bold_red = "\x1b[31;1m"  # Added bold for critical
    reset = "\x1b[0m"
    green = "\u001b[32m"
    bright_magenta = "\u001b[35;1m"

    def __init__(self, name: str):
        # Base format for console output
        # [Timestamp] Message
        super().__init__()
        self.str_format = f"[%(asctime)s][{name.upper()}]: %(message)s"

        # Dictionary mapping log levels to formatted strings with colors
        self.formats = {
            logging.DEBUG: self.bright_magenta + self.str_format + self.reset,
            logging.INFO: self.bright_green + self.str_format + self.reset,
            logging.WARNING: self.yellow + self.str_format + self.reset,
            logging.ERROR: self.red + self.str_format + self.reset,
            logging.CRITICAL: self.bold_red + self.str_format + self.reset
        }

    def format(self, record):
        """
        Formats the log record with the appropriate color based on its level.
        """
        # Get the format string for the current log record's level
        log_fmt = self.formats.get(record.levelno)
        # Create a new formatter with the specific format string
        formatter = logging.Formatter(log_fmt)
        # Format the record and return
        return formatter.format(record)


def logger(logs_dir: str = 'logs', log_file_name: str = 'app.log', name: str = 'DEFAULT'):
    """
    Configures and returns a logger instance for daily rotating logs.

    Args:
        logs_dir (str): The directory where log files will be stored.
                        Defaults to 'logs'.
        log_file_name (str): The base name for the log file.
                             Defaults to 'app.log'.
        name (str): The unique name for the logger instance.
    Returns:
        logging.Logger: The configured logger instance.
    """
    # Get or create the logger instance. Using the provided 'name' ensures a
    # unique logger for each module/purpose, preventing handler duplication.
    with SEM:
        logger = logging.getLogger(name)
        logger.setLevel(level=logging.DEBUG)

        # Prevent adding duplicate handlers if the logger is called multiple times
        # with the same name.
        if not logger.handlers:
            # Create the log directory if it doesn't exist
            full_logs_path = fr'{get_project_root()}/{logs_dir}'
            makedirs(full_logs_path, exist_ok=True)
            log_file_path = fr'{full_logs_path}/{log_file_name}'

            # Create a StreamHandler for console output
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.DEBUG)
            stream_handler.setFormatter(CustomFormatter(name))

            # Check if we already have a shared file handler for this file
            if log_file_path not in _shared_file_handlers:
                # Create a TimedRotatingFileHandler for daily log rotation
                file_handler = TimedRotatingFileHandler(
                    log_file_path,
                    when='midnight',
                    interval=1,
                    backupCount=7,
                    encoding='utf-8'
                )
                file_handler.setLevel(logging.DEBUG)

                # Define the format for log messages written to the file
                file_format = logging.Formatter(
                    "[%(asctime)s] [%(filename)s:%(lineno)d] [%(levelname)s] [%(name)s]: %(message)s"
                )
                file_handler.setFormatter(file_format)

                _shared_file_handlers[log_file_path] = file_handler
            else:
                file_handler = _shared_file_handlers[log_file_path]

            # Add the handlers to the logger
            logger.addHandler(stream_handler)
            logger.addHandler(file_handler)

        return logger


if __name__ == "__main__":
    # Demonstrate creating two separate loggers
    amazon_log = logger(name='AMAZON')
    report_log = logger(name='REPORT_GEN')

    amazon_log.info("This is an Amazon log message.")
    report_log.info("This is a Report Gen log message.")
    amazon_log.error("An error from the Amazon module.")
    report_log.warning("A warning from the Report Gen module.")
