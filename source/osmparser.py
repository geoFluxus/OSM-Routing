from tkinter import *
from math import floor
from source.utils import print


class OSMparser():
    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self.inv = {}  # node inventory
        self.nodes = {}
        self.ways = {}
        # OSM highway tags
        self.tags = {
            'motorway': 1,
            'trunk': 1,
            'primary': 1,
            'secondary': 1,
            'tertiary': 0,
            'motorway_link': 1,
            'trunk_link': 1,
            'primary_link': 1,
            'secondary_link': 1,
            'tertiary_link': 0
        }

    def readfile(self):
        # Open file
        try:
            with open(self.filename, "rb") as f:
                rows = sum(1 for _ in f)
            print(f'Total: {rows} lines')
        except FileNotFoundError:
            raise FileNotFoundError('File not found...')

        # Process file in two passes
        # first pass: process ways
        # second pass: process nodes
        for mode in range(2):
            msg = 'Processing nodes...' if mode else 'Processing ways...'
            print(msg)

            if not mode:
                self.render_tag_menu()

            self.file = open(self.filename, 'r', encoding="utf8")
            line = self.file.readline()
            row = 1
            while line:
                # progress
                if row % 100000 == 0:  # progress bar slow...
                    progress = row / rows * 100
                    print('Progress: {:.1f}%'.format(
                        progress), end="\r", flush=True)

                # mode 0: process ways
                # mode 1: process nodes
                if mode:
                    self.process_node(line)
                else:
                    row = self.process_way(line, row)

                # proceed
                row += 1
                line = self.file.readline()

            # CLOSE file
            self.file.close()
        msg = 'Result: {ways} ways, {nodes} nodes'.format(ways=len(self.ways),
                                                          nodes=len(self.nodes))
        print(msg)

    # process ways
    def process_way(self, line, row):
        if '<way' in line:
            found = False

            # read id
            id = line.replace('<way id="', '') \
                     .replace('">', '') \
                     .strip('\t') \
                     .strip('\n')

            # initialize refs
            refs = []

            # recover all node refs
            while '</way>' not in line:
                # read node ref
                row += 1
                line = self.file.readline()

                if '<nd' in line:
                    # check ref
                    ref = line.replace('<nd ref="', '') \
                              .replace('"/>', '') \
                              .strip('\t') \
                              .strip('\n')

                    # append to refs
                    refs.append(ref)
                elif '<tag' in line:
                    # check tag
                    tag = line.replace('<tag', '') \
                              .replace('/>', '') \
                              .strip('\t') \
                              .strip('\n') \
                              .split()

                    # get key & value
                    key = tag[0].strip('k=').strip('"')
                    value = tag[1].strip('v=').strip('"')

                    # check highway tag
                    if key == 'highway':
                        if value in self.tags and \
                           self.tags[value]:
                            found = True
                        break

            # if tag is found, then
            if found:
                # append way with references
                self.ways[id] = refs

                # append refs to node inventory to recover later
                for ref in refs:
                    self.inv[ref] = True

        return row

    # process nodes
    def process_node(self, line):
        if '<node' in line:
            # recover tags
            tags = line.replace('<node ', '') \
                       .replace('>', '') \
                       .replace('/', '') \
                       .split()

            # check if node belongs to way
            id = tags[0].strip('id=').strip('"')
            belongs = self.inv.get(id, False)

            # if belongs, process
            if belongs:
                lat = float(tags[1].strip('lat=').strip('"'))
                lon = float(tags[2].strip('lon=').strip('"'))
                self.nodes[id] = (lat, lon)

    def render_tag_menu(self):
        # initialize menu
        root = Tk()
        width, height = 260, 280
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        root.geometry('%dx%d+%d+%d' % (width, height, x, y))
        root.title('OSM Highway Tags')

        # render tags
        row, column = 0, 0
        n = floor(len(self.tags) / 2)
        variables, buttons = [], []
        for tag in self.tags:
            var = IntVar(root, value=self.tags[tag])
            button = Checkbutton(root, text=tag, variable=var)
            button.grid(row=row, column=column, pady=5, sticky='w')
            row += 1
            if row >= n:
                column = 1
                row -= n
            variables.append(var)
            buttons.append(button)

        def quit():
            for tag, var in zip(self.tags, variables):
                self.tags[tag] = var.get()
            root.quit()
            root.withdraw()

        def select():
            for button in buttons:
                button.select()

        def deselect():
            for button in buttons:
                button.deselect()

        # extra buttons (continue, select etc.)
        Button(root, text='Continue', command=quit).grid(
            row=n + 1, column=0, padx=20, pady=20)
        Button(root, text='Select all', command=select).grid(
            row=n + 2, column=0, padx=20)
        Button(root, text='Quit', command=exit).grid(
            row=n + 1, column=1, padx=20, pady=20)
        Button(root, text='Deselect all', command=deselect).grid(
            row=n + 2, column=1, padx=20)

        root.mainloop()
