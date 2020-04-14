from source.osmparser import OSMparser
from source.wktparser import WKTparser
from source.simplify import Simplify
from source.pgrouter import PgRouter
from source.utils import (export_lines,
                          export_points,
                          ask_input)
from tkinter import (messagebox,
                     filedialog,
                     Tk)
import os


############################################################################
# START MENU
############################################################################
# check OS
if os.name == 'nt':
    path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
elif os.name == 'posix':
    path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
else:
    raise ValueError('OS not supported...')

# open file menu
root = Tk()
root.withdraw()
root.filename = filedialog.askopenfilename(initialdir=path,
                                           title="Select file",
                                           filetypes=(("OSM", "*.osm"),
                                                      (("CSV (Comma Separated Values"), "*.csv"),
                                                      ("all files", "*.*")))
############################################################################


############################################################################
# OSM PARSER
############################################################################
# retrieve filename
filename = root.filename

if filename.endswith('.osm'):
    # parse file
    parser = OSMparser(filename)
    print('File: {}'.format(filename))
    print('Parsing file...', end="\r", flush=True)
    parser.readfile()
    print('Parsing complete...\n')

    # recover network
    network = {}
    network['ways'] = parser.ways
    network['nodes'] = parser.nodes
############################################################################


############################################################################
# SIMPLIFICATION
############################################################################
    # define epsg
    res = input('Provide EPSG to transform (default=4326): ')
    epsg = 4326 if not res else int(res)

    # initialize simplification
    res = input('Enter simplification resolution in EPSG units (default=0.01 degrees): ')
    resolution = 0.01 if not res else float(res)
    simplify = Simplify(network, epsg, resolution)

    # check (stringify OR simplify?)
    print('Simplification started...', end="\r", flush=True)

    # simplification
    simplify.stringify()
    simplify.simplify()

    # export file
    def export(name):
        print('Simplification complete...')
        print('Network exported in desktop...\n')
        export_lines(path, name, simplify.segments)
    name = os.path.basename(filename)
    export(name + '-simplified')

    segments = simplify.segments
############################################################################


############################################################################
# WKT PARSER
############################################################################
elif filename.endswith('.csv'):
    print('CSV file found...')
    parser = WKTparser(filename)
    print('File: {}'.format(filename))
    print('Parsing file...', end="\r", flush=True)
    parser.readfile()
    print('Parsing complete...\n')
    segments = parser.segments

    res = input('Enter snapping threshold (default=0.01 degrees): ')
    resolution = 0.01 if not res else float(res)
############################################################################


############################################################################
# DATABASE CONNECTION
############################################################################
res = ask_input('save to database')
if res:
    print('Storing network to database...\n')

    # request db credentials
    print('Enter database credentials...')
    print('To skip option, press "Enter"')
    database = input('- DB_NAME: ')
    user = input('- DB_USER: ')
    password = input('- DB_PASS: ')
    host = input('- DB_HOST (optional): ') or 'localhost'
    port = input('- DB_PORT (optional): ') or 5432

    # connect to database
    pgrouter = PgRouter(database=database,
                        user=user,
                        password=password,
                        host=host,
                        port=port,
                        threshold=resolution)
    pgrouter.create_network(segments)
    pgrouter.close_connection()
############################################################################

