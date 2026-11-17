# READING THE .map FILE
def read_map(filename):
    lines = []
    file = open(filename, "r")
    for line in file:
        lines.append(line.strip()) # remove the newline at the end
    file.close() # close the file, after reading

    height = int(lines[1].split()[1]) # "height 49" -> 49
    width = int(lines[2].split()[1]) # "width 49" -> 49

    grid = []
    for i in range(4, 4 + height): # map rows start after the 4 header lines (type, height, width, map)
        grid.append(lines[i])
    return height, width, grid

# READING THE .scen FILE
def read_scen(filename):
    scenarios = [] # each one is [bucket, start, goal, optimal length]
    file = open(filename, "r")
    for line in file:
        line = line.strip() # remove newline/spaces
        if line == "" or line.startswith("version"):
            continue # skip empty lines and the "version 1" header
        values = line.split() # columns are separated by tabs
        bucket = int(values[0])
        start = (int(values[4]), int(values[5])) # (x, y), x = column, y = row
        goal = (int(values[6]), int(values[7]))
        optimal = float(values[8]) # precomputed optimal path length
        scenarios.append([bucket, start, goal, optimal])
    file.close() # close the file, after reading
    return scenarios

# PICKING sample_size SCENARIOS SPREAD EVENLY ACROSS THE .scen FILE
def pick_scenarios(scenarios, sample_size):
    if sample_size >= len(scenarios):
        return scenarios # not enough scenarios, so just use all of them

    # the .scen file is sorted from easiest (bucket 0) to hardest, so taking every step-th one
    # gives a mix of short and long paths, and it's the same scenarios every run (reproducible)
    step = len(scenarios) / sample_size
    chosen = []
    for i in range(sample_size):
        chosen.append(scenarios[int(i * step)])
    return chosen