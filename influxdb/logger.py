import logging
import sys

logger_name = 'default'

def setup_logger(name, level):

    global logger_name
    logger_name = name

    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, level.upper()))

    # create console handler and set level to debug
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(getattr(logging, level.upper()))

    # create formatter
    formatter = logging.Formatter('[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger

def get_logger():

    global logger_name
    return logging.getLogger(logger_name)
