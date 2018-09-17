import pyodbc
import pandas as pd
import logging
import sys
from src.PriceEstimator.constants import database_password
from src.PriceEstimator.logger import create_loggers_helper


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


class DatabaseHandler:
    def __init__(self, server='', user_name='', database_name='', connection_string=''):
        if connection_string != '':
            logger.debug('Connecting to the database with connection string.')
            self.conn = pyodbc.connect(connection_string)
        else:
            try:
                self.conn = pyodbc.connect(server, user_name, database_password, database_name)
            except pyodbc.OperationalError:
                logger.error('Check the connection constants in constants.py file.')
                sys.exit(1)
            self.cursor = self.conn.cursor()
        self.cursor = self.conn.cursor()

    def execute_query(self, query):
        # self.cursor.execute(query) jak to odkomentuje, to program wywala blad:
        # pyodbc.Error: ('HY000', '[HY000] [Microsoft][SQL Server Native Client 11.0]Connection
        # is busy with results for another command (0) (SQLExecDirectW)
        logger.debug('Execute SQL query')
        return pd.read_sql(query, self.conn)

    def close_connection(self):
        self.conn.close()

