import logging
import pathlib


def create_logger(name_="Server"):
    logger = logging.getLogger(name_)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s:%(module)s:%(levelname)s:%(message)s %(funcName)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # console logger
    if not logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    return logger


def error_logger(func):
    logger = create_logger("aws")

    def wrapper(self, *args, **kwargs):
        try:
            res = func(self, *args, **kwargs)
            return res

        except Exception as e:
            logger.exception(f"Error Occured in {func.__name__} \n {e}")
            raise e

    return wrapper
