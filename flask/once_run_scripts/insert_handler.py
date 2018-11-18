from static.DatabaseHandler import DatabaseHandler

from flask.static.utils import get_db_connection


class Configuration:
    def __init__(self, filename) -> None:
        f= open(filename,"r")
        conf_str = f.read()
        f.close()
        conf_list = conf_str.split(", ")
        conf_dict = {}
        for c in conf_list:
            tmp = c.split(": ")
            key = tmp[0]
            value = tmp[1]
            conf_dict[key] = value
        self.netsize = conf_dict['netsize']
        self.south = conf_dict['south']
        self.north = conf_dict['north']
        self.east = conf_dict['east']
        self.west = conf_dict['west']
        self.xcoordsstep = conf_dict['xcoordsstep']
        self.ycoordsstep = conf_dict['ycoordsstep']
        self.xsidelength = conf_dict['xsidelength']
        self.ysidelength = conf_dict['ysidelength']


def insert_configuration_to_db(c, db):
    insert_statement = "insert into dbo.conf(netsize, south, north, east, west, xcoordsstep, ycoordsstep, xsidelength, ysidelength) values ({}, {}, {}, {}, {}, {}, {}, {}, {})".format(
                            c.netsize, c.south, c.north, c.east, c.west, c.xcoordsstep, c.ycoordsstep, c.xsidelength, c.ysidelength
                        )
    db.execute_statement(insert_statement)
    db.conn.commit()


def insert_altitudes(db):
    pass


def main():
    # db = DatabaseHandler('89.69.106.183:50002', 'agh', 'agh', 'LosAngelesCounty')
    db = get_db_connection()
    c = Configuration("xconf.txt")
    # insert_configuration_to_db(c, db)

    insert_altitudes(db)
    try:
        i = 0
        while(True):
            filename = "yinsert{}.txt".format(i)
            print(filename)
            f = open(filename, "r")
            lines = f.readlines()
            f.close()
            length = len(lines)
            step = 4000
            for j in range(0,length,step):
                insert_statement = ""
                for line in lines[j:j + step]:
                    insert_statement += line
                db.execute_statement(insert_statement)
            db.conn.commit()
            i += 1
    except FileNotFoundError:
        print("No more files found")




if __name__ == "__main__":
    main()


