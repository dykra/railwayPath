import pymssql as pymssql


class DatabaseHandler:

    def __init__(self, server, user, password, database_name):
        self.conn = pymssql.connect(server, user, password, database_name)
        self.cursor = self.conn.cursor()

    def execute_statement(self, string_statement):
        self.cursor.execute(string_statement)
        return self.cursor

    def close_connection(self):
        self.conn.close()