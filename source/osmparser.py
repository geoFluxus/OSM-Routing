class OSMparser():
    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self.nodes = {}
        self.ways = {}

    def readfile(self):
        # Open file
        try:
            with open(self.filename) as f:
                rows = sum(1 for _ in f)
        except FileNotFoundError:
            raise FileNotFoundError('File not found...')

        # Process file in two passes
        # first pass: process ways
        # second pass: process nodes
        for mode in range(2):
            msg = 'Processing nodes...' if mode else 'Processing ways...'
            print(msg)

            self.file = open(self.filename, 'r')
            line = self.file.readline()
            row = 1
            while line:
                # progress
                if row % 100000 == 0: # progress bar slow...
                    progress = row / rows * 100
                    print('Progress: {:.1f}%'.format(progress), end="\r", flush=True)

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
                row += 1
                line = self.file.readline()
                if '<nd' not in line: break
                ref = line.replace('<nd ref="', '') \
                    .replace('"/>', '') \
                    .strip('\t') \
                    .strip('\n')
                # append to way
                self.ways[id].append(ref)
        return row

    # process nodes
    def process_node(self, line):
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