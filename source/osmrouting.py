from osmparser import OSMparser
from simplify import Simplify
from pgrouter import PgRouter
from utils import (export_lines,
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
                                                      ("all files", "*.*")))
############################################################################


############################################################################
# FILE PARSER
############################################################################
# retrieve filename
filename = root.filename

# parse file
parser = OSMparser(filename)
print('File: {}'.format(filename))
print('Parsing file...')
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
# initialize simplification
simplify = Simplify(network)

# check (stringify OR simplify?)
print('Simplification started...')
resp = ask_input('- just stringify')

# export file
def export(name):
    print('Network exported in desktop...')
    export_lines(path, name, simplify.segments)
    print('Simplification complete...\n')

# simplification
simplify.stringify() # need it in any case...
name = os.path.basename(filename)
if resp:
    export(name + '-stringified')
else:
    simplify.simplify()
    export(name + '-simplified')
############################################################################


############################################################################
# DATABASE CONNECTION
############################################################################
res = ask_input('save to database')
if res:
    print('Storing network to database...\n')

    # request db credentials
    print('Enter database credentials...')
    database = input('- DB_NAME: ')
    user = input('- DB_USER: ')
    password = input('- DB_PASS: ')
    host = input('- DB_HOST: ') or 'localhost'
    port = input('- DB_PORT: ') or 5432

    # connect to database
    pgrouter = PgRouter(database=database,
                        user=user,
                        password=password,
                        host=host,
                        port=port)
    pgrouter.create_network(simplify.segments)
    pgrouter.close_connection()
############################################################################


