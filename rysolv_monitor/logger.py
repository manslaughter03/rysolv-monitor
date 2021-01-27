"""

logger module
"""
import logging


def configure_logger(name: str, level: int) -> logging.Logger:
    """

    configure logger
    :param name:
    :param level:
    :return:
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # create console handler and set level to debug
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to stream_handler
    stream_handler.setFormatter(formatter)

    # add stream_handler to logger
    logger.addHandler(stream_handler)

    return logger
