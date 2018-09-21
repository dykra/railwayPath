import pymssql
import pandas as pd
import logging
import sys
from src.priceestimation.database_connection_constants import database_password
from src.priceestimation.utils.logger import create_loggers_helper


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


class DatabaseHandler:
    def __init__(self,
                 server='',
                 user_name='',
                 database_name=''):
        try:
            self.conn = pymssql.connect(server=server,
                                        user=user_name,
                                        password=database_password,
                                        database=database_name)
        except pymssql.OperationalError:
            logger.error('Not all parameters to '
                         'connect with database are provided.')
            sys.exit(1)
        self.cursor = self.conn.cursor()

    def execute_query(self, query):
        self.cursor.execute(query)
        logger.debug('Reading data from database')
        return pd.read_sql(query, self.conn)

    def close_connection(self):
        self.conn.close()
