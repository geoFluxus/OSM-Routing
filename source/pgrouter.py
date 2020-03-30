import psycopg2 as pg
from source.utils import (ask_input,
                          export_lines)
from source.geom import extent
from source.snapper import Snapper

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
            try:
                return self.cursor.fetchall()
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

    # create ways
    def create_ways(self):
        # create non-geometric fields
        query = """
                CREATE TABLE IF NOT EXISTS ways (
                    id BIGINT PRIMARY KEY,
                    source INTEGER,
                    target INTEGER
                )
                """
        self.execute(query)

        # check geometry column
        query = """
                SELECT column_name
                FROM information_schema.columns 
                WHERE table_name='ways' and column_name='the_geom';
                """
        if not self.execute(query):
            # create geometry column
            query = """
                    SELECT AddGeometryColumn('public', 'ways', 
                    'the_geom', 4326, 'LINESTRING', 2);
                    """
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

        # option to clear existent database
        resp = ask_input('- clear database')
        if resp:
            resp = ask_input('- are you sure')
            if resp:
                self.drop_table('ways')
                self.drop_table('ways_vertices_pgr')

        # create ways table
        self.create_ways()

        # count existent rows
        query = 'SELECT COUNT(*) FROM ways'
        count = self.execute(query)[0][0]

        # if network already exists
        # snap simplified to it
        if count > 0:
            # do not recover all the network!
            # only the part close to the new addition

            # recover bbox of simplified
            bbox = extent(segments)
            # recover network intersecting the bbox
            query = \
                '''
                SELECT ST_AsText(the_geom)
                FROM ways
                WHERE ST_Intersects(
                    the_geom,
                    (SELECT ST_MakeEnvelope(%f, %f, %f, %f, 4326))
                )
                ''' % bbox
            ways = self.execute(query)

            # convert to geometry
            # reference to snap the new addition
            reference = []
            for way in ways:
                wkt = way[0]
                coords = wkt.strip('LINESTRING(')\
                            .strip(')') \
                            .replace(',', ' ') \
                            .split(' ')
                coords = [float(coord) for coord in coords]
                # lat, lon ordering
                edge = []
                for i in range(0, len(coords)-1, 2):
                    edge.append((coords[i+1], coords[i]))
                reference.append(edge)

            # if not reference, do not snap
            # the addition is irrelevant to existing network
            if len(reference) > 0:
                snapper = Snapper(segments, reference)
                snapper.point_snap()
                snapper.edge_snap()
                segments = snapper.segments

        # insert segments
        for segment in segments:
            # row number
            count += 1

            # form wkt
            wkt = 'LINESTRING('
            for point in segment:
                lat, lon = point
                wkt += '{} {},'.format(lon, lat)
            wkt = wkt[:-1] + ')'

            # insert query
            query = """
                    INSERT INTO ways (id, source, target, the_geom)
                    VALUES ({}, NULL, NULL, ST_GeomFromText('{}',4326))
                    """.format(count, wkt)
            self.execute(query)

        # create topology
        query = """
                SELECT
                pgr_createTopology('ways', 0.0001);
                """
        self.execute(query)



