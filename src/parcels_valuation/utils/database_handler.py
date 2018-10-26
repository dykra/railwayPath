import pymssql
import pandas as pd
import logging
import sys
from dotenv import load_dotenv
from src.parcels_valuation.utils.logger import create_loggers_helper
import os

load_dotenv()


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


class DatabaseHandler:
    def __init__(self,
                 server_name=os.getenv("SERVER_NAME"),
                 database_name=os.getenv("DATABASE_NAME"),
                 user_name=os.getenv("USER_NAME"),
                 database_password=os.getenv("DATABASE_PASSWORD")
                 ):
        try:
            self.conn = pymssql.connect(server=server_name,
                                        user=user_name,
                                        password=database_password,
                                        database=database_name)
        except pymssql.OperationalError:
            logger.error('Error while connecting to database. Check all the parameters.')
            sys.exit(1)
        self.cursor = self.conn.cursor()

    def execute_query(self, query):
        self.cursor.execute(query)
        logger.debug('Reading data from database')
        return pd.read_sql(query, self.conn)

    def close_connection(self):
        self.conn.close()