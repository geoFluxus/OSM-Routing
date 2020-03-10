class OSMparser():
    def __init__(self, filename):
        self.filename = filename
        self.nodes = {}
        self.ways = {}

    def readfile(self):
        # Open file
        try:
            fil = open(self.filename, 'r')
        except FileNotFoundError:
            raise FileNotFoundError('File not found...')

        line = fil.readline()
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

        # CLOSE file
        fil.close()