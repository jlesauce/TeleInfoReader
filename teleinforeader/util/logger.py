import logging
import sys

DEFAULT_LOG_LEVEL = logging.INFO


def configure_logger(log_file: str = None, log_level=DEFAULT_LOG_LEVEL):
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)s.%(funcName)s]: %(message)s')
    logger = logging.getLogger()
    configure_application_log_level(log_level)

    if log_file:
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

    logger.setLevel(log_level)


def configure_application_log_level(log_level):
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logging.getLogger('matplotlib').setLevel(logging.ERROR)
