from tkinter import filedialog
from tkinter import *
import os


class OSMparser():
    def __init__(self):
        self.nodes = {}
        self.ways = {}
        self.path = ''

    def readfile(self):
        # Check OS
        if os.name == 'nt':
            self.path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        elif os.name == 'posix':
            self.path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
        else:
            raise ValueError('OS not supported...')

        # Menu to open file
        root = Tk()
        root.filename = filedialog.askopenfilename(initialdir=self.path,
                                                   title="Select file",
                                                   filetypes=(("OSM", "*.osm"),
                                                              ("all files", "*.*")))

        # File to be processed
        filename = root.filename

        # Open file
        try:
            fil = open(filename, 'r')
        except FileNotFoundError:
            raise FileNotFoundError('File not found...')

        # Skip the first lines
        for i in range(3):
            line = fil.readline()

        print('Parsing file...')
        while line:
            line = fil.readline()

            # process nodes
            if '<node' in line:
                # recover tags
                tags = line.replace('<node ', '') \
                    .replace('>', '') \
                    .replace('/', '') \
                    .split()

                # id / lat /lon
                id = tags[0].strip('id=').strip('"')
                lat = float(tags[1].strip('lat=').strip('"'))
                lon = float(tags[2].strip('lon=').strip('"'))
                self.nodes[id] = (lat, lon)

            # process ways
            if '<way' in line:
                # read id
                id = line.replace('<way id="', '') \
                    .replace('">', '') \
                    .strip('\t') \
                    .strip('\n')
                # initialize way
                self.ways[id] = []
                # recover all node refs
                while '</way>' not in line:
                    # read node ref
                    line = fil.readline()
                    if '<nd' not in line: break
                    ref = line.replace('<nd ref="', '') \
                        .replace('"/>', '') \
                        .strip('\t') \
                        .strip('\n')
                    # append to way
                    self.ways[id].append(ref)
        print('Parsing complete...')

        # CLOSE file
        fil.close()