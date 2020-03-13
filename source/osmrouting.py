from osmparser import OSMparser
from simplify import Simplify
from pgrouter import PgRouter
from utils import (export_lines,
                   export_points)
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
filename = root.filename

# parse file
parser = OSMparser(filename)
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
resp = input('Just STRINGIFY? [Y/N] ') or 'n'
while resp.lower() not in ['y', 'n']:
    resp = input('Just STRINGIFY? [Y/N] ')

# export file
def export(name):
    resp = input('Export {} network? [Y/N] '.format(name.upper())) or 'n'
    while resp.lower() not in ['y', 'n']:
        resp = input('Export {} network? [Y/N] '.format(name.upper()))
    if resp == 'y':
        print('File exported in desktop...')
        export_lines(path, name, simplify.segments)
    print('Simplification complete...\n')

# simplification
simplify.stringify() # need it in any case...
if resp == 'y':
    export('stringified')
else:
    simplify.simplify()
    export('simplified')
############################################################################


############################################################################
# DATABASE CONNECTION
############################################################################
print('Store network to database...')

# request db credentials
print('Enter database credentials...')
database = input('DB_NAME: ')
user = input('DB_USER: ')
password = input('DB_PASS: ')
host = input('DB_HOST: ') or 'localhost'
port = input('DB_PORT: ') or 5432

# connect to database
pgrouter = PgRouter(database=database,
                    user=user,
                    password=password,
                    host=host,
                    port=port)
pgrouter.close_connection()
############################################################################


