import psycopg2 as pg
from utils import ask_input

class PgRouter():
    def __init__(self, database, user, password,
                 host='localhost',
                 port=5432):
        # database credentials
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port

        # connection
        self.connection = None
        self.cursor = None
        self.open_connection() # assert connection
        self.check_postgis() # assert postgis
        self.check_pgrouting() # assert pgrouting

    # connect to db
    def open_connection(self):
        try:
            self.connection = pg.connect(database=self.database,
                                         user=self.user,
                                         password=self.password,
                                         host=self.host,
                                         port=self.port)
            self.cursor = self.connection.cursor()
            print('Connection established...\n')
        except (Exception, pg.Error) as error:
            print('Connection failed...')
            print(error)
            exit()

    # close connection
    def close_connection(self):
        self.cursor.close()
        self.connection.close()
        print('Connection closed...')

    # execute query
    def execute(self, query):
        try:
            self.cursor.execute(query)
            try:
                result = self.cursor.fetchall()
                return result
            except:
                return
        except (Exception, pg.Error) as error:
            print('Error occured...', error)
            self.close_connection()  # KILL CONNECTION!
            exit() # exit program

    # check postGIS
    def check_postgis(self):
        query = 'SELECT PostGIS_version();'
        self.execute(query)

    # check pgrouting
    def check_pgrouting(self):
        query = 'SELECT pgr_version();'
        self.execute(query)

    # check if tables exists
    def exists_table(self, name):
        # assume that everything is stored in public schema...
        query = """
                SELECT * FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME = '{}'
                """.format(name)
        return self.execute(query)

    # create table
    def create_table(self, table):
        name, fields = table['name'], table['fields']
        if not self.exists_table(name):
            fields = ','.join(fields)
            query = """
                    CREATE TABLE {name} (
                        {fields}
                    )
                    """.format(name=name, fields=fields)
            self.execute(query)
            self.connection.commit()
            return False
        else:
            return True

    # drop table
    def drop_table(self, name):
        if self.exists_table(name):
            print('drop')
            query = 'DROP TABLE {}'.format(name)
            self.execute(query)
            self.connection.commit()

    # flush table
    def flush_table(self, name):
        if self.exists_table(name):
            query = 'DELETE from {}'.format(name)
            self.execute(query)
            self.connection.commit()

    # create network tables
    def create_network(self):
        # start forming network
        print('Create pgRouting database...')

        # define tables
        ways = {'name': 'ways',
                'fields': ['id SERIAL PRIMARY KEY']}
        nodes = {'name': 'nodes',
                 'fields': ['id SERIAL PRIMARY KEY']}

        # clear existent database
        resp = ask_input('- clear database')
        if resp:
            resp = ask_input('ARE YOU SURE')
            if resp:
                self.drop_table(ways['name']) # ways
                self.drop_table(nodes['name']) # nodes

        # create tables
        # check if only one table exists
        # if self.create_table(ways) != self.create_table(nodes):
        #     print('One of the tables already exists, this may cause problems..')


