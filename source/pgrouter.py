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
        self.create_extension('postgis') # assert postgis
        self.create_extension('pgrouting') # assert pgrouting

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

    # create extensions
    def create_extension(self, extension):
        query = 'CREATE EXTENSION IF NOT EXISTS {}'.format(extension)
        self.execute(query)
        self.connection.commit()

    # create table
    def create_table(self, table):
        name = table['name']
        fields = table['fields']
        type = table['type']

        # create non-geometric fields
        fields = ','.join(fields)
        query = """
                CREATE TABLE IF NOT EXISTS {name} (
                    {fields}
                )
                """.format(name=name, fields=fields)
        self.execute(query)
        self.connection.commit()

        # create geometry column
        query = """
                SELECT AddGeometryColumn('public', '{name}', 'the_geom', 4326, '{type}', 2);
                """.format(name=name, type=type)
        self.execute(query)
        self.connection.commit()

    # drop table
    def drop_table(self, name):
        query = 'DROP TABLE IF EXISTS {}'.format(name)
        self.execute(query)
        self.connection.commit()

    # flush table
    def flush_table(self, name):
        query = 'DELETE from {}'.format(name)
        self.execute(query)
        self.connection.commit()

    # create network tables
    def create_network(self):
        # start forming network
        print('Create pgRouting database...')

        # define tables
        ways = {'name': 'ways',
                'fields': ['id SERIAL PRIMARY KEY',
                           'source INTEGER',
                           'target INTEGER'],
                'type': 'LINESTRING'}
        nodes = {'name': 'nodes',
                 'fields': ['id SERIAL PRIMARY KEY'],
                 'type': 'POINT'}

        # option to clear existent database
        resp = ask_input('- clear database')
        if resp:
            resp = ask_input('- are you sure')
            if resp:
                self.drop_table(ways['name']) # ways
                self.drop_table(nodes['name']) # nodes

        # create tables
        self.create_table(ways)
        self.create_table(nodes)


