

# TODO przetestowa jeszcze raz to tworzenie loggerow czy dobrze mowi klase i


def create_loggers_helper(logger):
    import logging
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger


def create_loggers():
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    logger = create_loggers_helper(logger)
    return logger