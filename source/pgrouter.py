import psycopg2 as pg


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
        self.open_connection()
        self.check_postgis()
        self.check_pgrouting()

    # connect to db
    def open_connection(self):
        try:
            self.connection = pg.connect(database=self.database,
                                         user=self.user,
                                         password=self.password,
                                         host=self.host,
                                         port=self.port)
            self.cursor = self.connection.cursor()
            print('Connection established...')
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

    # create tables
    def create_tables(self):
        # check if tables exists
        # assume that everything is stored in public schema...
        query = """
                SELECT * FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME = 'ways'
                """
        exists = self.execute(query)
        if not exists:
            query = """
                    CREATE TABLE ways (
                        id SERIAL PRIMARY KEY
                    )
                    """
            self.execute(query)
            self.connection.commit()
            print('Create ways...')
        else:
            print('Update ways...')

