from osmparser import OSMparser
from simplify import Simplify
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
# FILE PARSER #
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
# SIMPLIFICATION #
############################################################################
# initialize simplification
simplify = Simplify(network)

# check (stringify OR simplify?)
msgbox = messagebox.askquestion('WARNING!',
                                'Just STRINGIFY?')

# export file
def export(name):
    msgbox = messagebox.askquestion('Export file',
                                    'Want to export {} network?'.format(name))
    if msgbox == 'yes':
        messagebox.showinfo('Message',
                            'File exported in desktop...')
        export_lines(path, name, simplify.segments)
    print('Simplification complete...\n')

# simplification
print('Simplification started...')
simplify.stringify() # need it in any case...
if msgbox == 'yes':
    export('stringified')
else:
    simplify.simplify()
    export('simplified')
############################################################################


