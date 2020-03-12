class OSMparser():
    def __init__(self, filename):
        self.filename = filename
        self.nodes = {}
        self.ways = {}

    def readfile(self):
        # Open file
        try:
            with open(self.filename) as f:
                rows = sum(1 for _ in f)
            fil = open(self.filename, 'r')
        except FileNotFoundError:
            raise FileNotFoundError('File not found...')

        line = fil.readline()
        row = 1
        while line:
            # progress
            if row % 100000 == 0: # progress bar slow...
                progress = row / rows * 100
                print('Progress: {:.1f}%'.format(progress), end="\r", flush=True)
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
                    row += 1
                    line = fil.readline()
                    if '<nd' not in line: break
                    ref = line.replace('<nd ref="', '') \
                        .replace('"/>', '') \
                        .strip('\t') \
                        .strip('\n')
                    # append to way
                    self.ways[id].append(ref)

            # proceed
            row += 1
            line = fil.readline()

        # CLOSE file
        fil.close()