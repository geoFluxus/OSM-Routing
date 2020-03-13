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
            self.connection.commit()
        except (Exception, pg.Error) as error:
            print('Error occured...', error)
            self.close_connection()  # KILL CONNECTION!
            exit() # exit program

    # create extensions
    def create_extension(self, extension):
        query = 'CREATE EXTENSION IF NOT EXISTS {}'.format(extension)
        self.execute(query)

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

        # create geometry column
        query = """
                SELECT AddGeometryColumn('public', '{name}', 'the_geom', 4326, '{type}', 2);
                """.format(name=name, type=type)
        self.execute(query)

    # drop table
    def drop_table(self, name):
        query = 'DROP TABLE IF EXISTS {}'.format(name)
        self.execute(query)

    # flush table
    def flush_table(self, name):
        query = 'DELETE from {}'.format(name)
        self.execute(query)

    # create network tables
    def create_network(self, segments):
        # start forming network
        print('Create pgRouting database...')

        # define tables
        ways = {'name': 'ways',
                'fields': ['id SERIAL PRIMARY KEY',
                           'source INTEGER',
                           'target INTEGER'],
                'type': 'LINESTRING'}

        # option to clear existent database
        resp = ask_input('- clear database')
        if resp:
            resp = ask_input('- are you sure')
            if resp:
                self.drop_table('ways')
                self.drop_table('ways_vertices_pgr')

        # create ways table
        self.create_table(ways)

        # insert segments
        for segment in segments:
            # form wkt
            wkt = 'LINESTRING('
            for point in segment:
                lat, lon = point
                wkt += '{} {},'.format(lon, lat)
            wkt = wkt[:-1] + ')'

            # insert query
            query = """
                    INSERT INTO ways (source, target, the_geom)
                    VALUES (NULL, NULL, ST_GeomFromText('{}',4326))
                    """.format(wkt)
            self.execute(query)

        # create topology
        query = """
                SELECT
                pgr_createTopology('ways', 0.0001);
                """
        self.execute(query)



