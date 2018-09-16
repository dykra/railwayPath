def create_loggers_helper(logger):
    import logging
    # create console handler and set level to debug
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    console_handler.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(console_handler)
    return logger
