import os


# LISTING ALL .map NAMES IN A FOLDER (MATCHED WITH THEIR .map.scen FILE)
def list_maps(map_dir, scen_dir):
    names = []
    for filename in sorted(os.listdir(map_dir)):
        if filename.endswith(".map"):
            scen_path = os.path.join(scen_dir, filename + ".scen")
            if os.path.exists(scen_path):
                names.append(filename[:-4]) # strip the ".map" extension
    return names

# READING THE .map FILE
def read_map(filename):
    lines = []
    with open(filename, "r") as file:
        for line in file:
            lines.append(line.strip()) # remove the newline at the end

    height = int(lines[1].split()[1]) # "height 49" -> 49
    width = int(lines[2].split()[1]) # "width 49" -> 49

    grid = []
    for i in range(4, 4 + height): # map rows start after the 4 header lines (type, height, width, map)
        grid.append(lines[i])
    return height, width, grid

# READING THE .scen FILE
def read_scen(filename):
    scenarios = [] # each one is [bucket, start, goal, optimal length]
    with open(filename, "r") as file:
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
    return scenarios

# PICKING sample_size SCENARIOS SPREAD EVENLY ACROSS THE .scen FILE
def pick_scenarios(scenarios, sample_size):
    if sample_size >= len(scenarios):
        return scenarios # not enough scenarios, so just use all of them
    if sample_size == 1:
        return [scenarios[len(scenarios) // 2]]

    # the .scen file is sorted from easiest (bucket 0) to hardest, so spacing indices evenly
    # from 0 to len - 1 gives a reproducible mix spanning easiest to hardest
    step = (len(scenarios) - 1) / (sample_size - 1)
    chosen = []
    for i in range(sample_size):
        chosen.append(scenarios[round(i * step)])
    return chosen