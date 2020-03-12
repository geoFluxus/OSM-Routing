from osmparser import OSMparser
from simplify import Simplify
from utils import export_lines, export_points
from tkinter import (messagebox,
                     filedialog,
                     Tk)
import os


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
root.destroy()
filename = root.filename

# parse file
parser = OSMparser(filename)
print('[PROCESS] Parse OSM')
print('Parsing file...')
parser.readfile()
print('Parsing complete...')
print('[END PROCESS]\n')

# recover network
network = {}
network['ways'] = parser.ways
network['nodes'] = parser.nodes

# initialize simplification
print('[PROCESS] Simplification')
simplify = Simplify(network)

# check (stringify OR simplify?)
root = Tk()
root.withdraw()
msgbox = messagebox.askquestion('WARNING!',
                                'Just STRINGIFY?')

# simplification
print('Simplification started...')
simplify.stringify() # need it in any case...
if msgbox == 'yes':
    # check to export stringify
    msgbox = messagebox.askquestion('Export file',
                                    'Want to export stringified network?')
    if msgbox == 'yes':
        messagebox.showinfo('Message',
                            'File exported in desktop...')
        export_lines(path, 'stringified', simplify.segments)
    print('Simplification complete...')
    print('[END PROCESS]\n')
    exit()
else:
    # simplify
    simplify.simplify()
    # check to export simplify
    msgbox = messagebox.askquestion('Export file',
                                    'Want to export simplified network?')
    if msgbox == 'yes':
        messagebox.showinfo('Message',
                            'File exported in desktop...')
        export_lines(path, 'stringified', simplify.segments)
    print('Simplification complete...')
    print('[END PROCESS]\n')


