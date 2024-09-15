import logging
from logging.handlers import RotatingFileHandler


def setup_logger(name, log_file, level=logging.INFO):
    handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


app_logger = setup_logger('app_logger', 'app.log')
error_logger = setup_logger('error_logger', 'error.log', level=logging.ERROR)