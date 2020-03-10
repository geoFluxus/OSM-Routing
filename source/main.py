from osmparser import OSMparser
from simplify import Simplify
from utils import export_lines, export_points
from tkinter import messagebox, filedialog, Tk
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
print('Parsing complete...\n')

# recover network
network = {}
network['ways'] = parser.ways
network['nodes'] = parser.nodes

# initialize simplification
print('[PROCESS] Simplification')
simplify = Simplify(network)

# record intersections
print('[STEP 1]')
print('Record intersections...')
simplify.record_intersections()
print('Intersections recorded...\n')
root = Tk()
root.withdraw()
# check to export intersections
msgbox = messagebox.askquestion('Export file',
                                'Want to export intersections?')
if msgbox == 'yes':
    messagebox.showinfo('Message',
                        'File exported in desktop...')
    intersections = simplify.intersections
    points = []
    for point, is_intersection in intersections.items():
        if is_intersection: points.append(point)
    export_points(path, 'intersections', points)


# stringify
print('[STEP 2]')
print('Stringify...')
simplify.stringify()
print('Stringify complete...\n')
root = Tk()
root.withdraw()
# check to export stringify
msgbox = messagebox.askquestion('Export file',
                                'Want to export stringified network?')
if msgbox == 'yes':
    messagebox.showinfo('Message',
                        'File exported in desktop...')
    export_lines(path, 'stringify', simplify.segments)


# clustering
print('[STEP 3]')
print('Cluster intersections...')
simplify.cluster()
clusters = simplify.clusters
cnum = 0
points, attrs = [], []
for cluster in clusters:
    for point in cluster:
        points.append(point)
        attrs.append(cnum)
    cnum += 1
export_points(path, 'clusters', points, attrs)
print('Clustering complete...\n')


# rebuild network
print('[STEP 4]')
print('Rebuild network...')
print('Network complete...\n')


