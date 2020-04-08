from source.osmparser import OSMparser
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
resolution = 0.01
simplify = Simplify(network, resolution)

# check (stringify OR simplify?)
print('Simplification started...')

# simplification
simplify.stringify()
simplify.simplify()

# export file
def export(name):
    print('Network exported in desktop...')
    export_lines(path, name, simplify.segments)
    print('Simplification complete...\n')
name = os.path.basename(filename)
export(name + '-simplified')
############################################################################


############################################################################
# DATABASE CONNECTION
############################################################################
# res = ask_input('save to database')
# if res:
# print('Storing network to database...\n')

# request db credentials
# print('Enter database credentials...')
# print('To ignore, press "Enter"')
# database = input('- DB_NAME: ')
# user = input('- DB_USER: ')
# password = input('- DB_PASS: ')
# host = input('- DB_HOST (optional): ') or 'localhost'
# port = input('- DB_PORT (optional): ') or 5432

# connect to database
pgrouter = PgRouter(database='streets',
                    user='postgres',
                    password='postgres',
                    host='localhost',
                    port='5432',
                    threshold=resolution)
pgrouter.create_network(simplify.segments)
pgrouter.close_connection()
############################################################################


