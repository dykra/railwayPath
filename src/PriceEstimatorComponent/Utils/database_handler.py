import pymssql
import pandas as pd
import logging
import sys
from src.PriceEstimatorComponent.constants import database_password
from src.PriceEstimatorComponent.Utils.logger import create_loggers_helper


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


class DatabaseHandler:
    def __init__(self, server='', user_name='', database_name='', connection_string=''):
        if connection_string != '':
            logger.debug('Connecting to the database with connection string.')
            self.conn = pymssql.connect(connection_string)
        else:
            try:
                self.conn = pymssql.connect(server, user_name, database_password, database_name)
            except pymssql.OperationalError:
                logger.error('Check whether all the parameters are correct. '
                             'Server, user name and database name are program inputs '
                             'and password should be specified in constants.py file.')
                sys.exit(1)
            self.cursor = self.conn.cursor()
        self.cursor = self.conn.cursor()

    def execute_statement(self, statement):
        self.cursor.execute(statement)
        logger.debug('Reading data from database')
        return pd.read_sql(statement, self.conn)

    def close_connection(self):
        self.conn.close()

