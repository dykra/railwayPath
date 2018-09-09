import pymssql
import pandas as pd
import getpass
import logging
from PriceEstimatorComponent.logger import create_loggers_helper


def create_loggers():
    logger1 = logging.getLogger(__name__)
    logger1.setLevel(logging.DEBUG)
    logger1 = create_loggers_helper(logger1)
    return logger1


logger = create_loggers()


class DatabaseHandler:
    def __init__(self, server, user_name, database_name):
        print('Provide SQL database password:')
        try:
            p = getpass.getpass()
        except Exception as err:
            logger.error(err)
            exit(1)
        else:
            self.conn = pymssql.connect(server, user_name, p, database_name)
            self.cursor = self.conn.cursor()

    def execute_statement(self, string_statement):
        self.cursor.execute(string_statement)
        return self.cursor

    def close_connection(self):
        self.conn.close()


def execute_sql_statement(server, user_name, database_name, statement):
    database_handler = DatabaseHandler(server, user_name, database_name)
    logger.debug('Reading data from database')
    return pd.read_sql(statement, database_handler.conn)