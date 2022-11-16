import logging
import sys

DEFAULT_LOG_LEVEL = logging.DEBUG


def configure_logger(log_file: str):
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)s.%(funcName)s]: %(message)s')
    logger = logging.getLogger()
    configure_application_log_level()

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)
    logger.addHandler(stdout_handler)

    stderr_handler = logging.StreamHandler()
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)

    logger.setLevel(DEFAULT_LOG_LEVEL)


def configure_application_log_level():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.getLogger('matplotlib').setLevel(logging.ERROR)
