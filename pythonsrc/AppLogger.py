import logging

common_logger = None


def get_logger():
    global common_logger
    if common_logger is None:
        common_logger = set_up_logger()

    return common_logger


def set_up_logger():
    logger = logging.getLogger('logAnomalyDetection')
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler('../logs/application.log')
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    logger.info('logger is set up')
    return logger
