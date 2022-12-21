import logging
import pathlib
def create_logger(name_="Server"):
    path = pathlib.Path(__file__).parent
    logger = logging.getLogger(name_)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s:%(module)s:%(levelname)s:%(message)s %(funcName)s', datefmt='%Y-%m-%d %H:%M:%S')

    #consol logger
    if not logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    #file logger
    log_file_name = 'log/scrap.log'
    file_handler = logging.FileHandler(path.joinpath(log_file_name))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
