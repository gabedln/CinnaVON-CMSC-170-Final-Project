'''
python file to plot results from results.csv to graph using matplotlib
'''

import csv  # to read the results.csv file

import matplotlib.pyplot as plt  # to plot the results

from load_map import read_map  # to get the dimensions of the map

# change font for graph 
plt.rcParams.update({'font.size': 12, 'font.family': 'Georgia'})
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'

# defining colors for each method
colors = {
    "UCS": "#1b4965",
    "A*": "#3a86b7",
    "Hill Climbing": "#8ecae6"
}
methods = ["UCS", "A*", "Hill Climbing"] # defining the methods that we are using

short_names = { # original game names are too long for graphs, so we use short names for the graphs
    "Baldur's Gate II (Original)" : "BG2 (Orig)",
    "Baldur's Gate II (512x512)" : "BG2 (512)",
    "Dragon Age: Origins" : "DAO",
    "Dragon Age II" : "DA2",
    "StarCraft" : "SC1",
    "Warcraft III (512x512)" : "WC3 (512)",
    "OVERALL" : "Overall"
}

map_folders = { # used to get dimension of the map
    "Baldur's Gate II (Original)" : "bgmaps-map",
    "Baldur's Gate II (512x512)" : "bg512-map",
    "Dragon Age: Origins" : "dao-map",
    "Dragon Age II" : "da2-map",
    "StarCraft" : "sc1-map",
    "Warcraft III (512x512)" : "wc3maps512-map"
}

# first we need to read file form our csv
def read_results(filename): # read results is for results.csv, 
    games = [] # summary per game, all maps and 10 scenarios per amp
    data = {} # data is a dictionary with methods as key
    for m in methods: # iterating per method
        data[m] = { # creates new key for each method, and the value is a dictionary with the following keys
            "success_rate": [],
            "optimality_rate": [],
            "avg_cost_ratio": [],
            "avg_nodes_expanded": [],
            "avg_peak_open": [],
            "avg_runtime_s": []
        }
    with open(filename, "r") as summary:
        for row in csv.DictReader(summary):
            game = row["game"]
            m = row["method"]
            if game not in games:
                games.append(game)
            data[m]["success_rate"].append(float(row["success_rate"]))
            data[m]["optimality_rate"].append(float(row["optimality_rate"]))
            data[m]["avg_cost_ratio"].append(float(row["avg_cost_ratio"]))
            data[m]["avg_nodes_expanded"].append(float(row["avg_nodes_expanded"]))
            data[m]["avg_peak_open"].append(float(row["avg_peak_open"]))
            data[m]["avg_runtime_s"].append(float(row["avg_runtime_s"]))
            # example access: data["UCS"]["avg_runtime_s"][0] gives the average runtime for UCS for the first game in games list
    return games, data

# ito ung pang 15k na lines (raW_results.csv), tapos pwede ring gawing plot
def read_all(filename):
    rows = []
    with open(filename, "r") as file:
        for row in csv.DictReader(file):
            rows.append({
                "game": row["game"],
                "map": row["map"],
                "method": row["method"],
                "found" : row["found"] == "True", # since it's string we convert it to boolean
                "cost": float(row["cost"]),
                "optimal": float(row["optimal"]),
                "nodes_expanded": int(row["nodes_expanded"]),
                "peak_open": int(row["peak_open"]),
                "runtime": float(row["runtime"]),
                "is_optimal": row["is_optimal"] == "True"
            })
    return rows

def get_labels(games): # helper function that gets shortenned label for game
    labels = [] # init
    for g in games: # for each game,
        if g in short_names: # if it's in short_names we append
            labels.append(short_names[g])
        else: # else we just append the whole game name
            labels.append(g)
    return labels

def get_dimensions(raw_data): # area computation, to show failure in hill climbing
    areas = {}
    for row in raw_data:
        key = (row["game"], row["map"])
        if key not in areas:
            path = map_folders[row["game"]] + "/" + row["map"] + ".map" # get the path to the map file
            h, w, _ = read_map(path) # read the map file to get height and width
            areas[key] = h * w # compute area
    return areas

def draw_three_bars(games, data, column):
    x = list(range(len(games)))     # [0, 1, 2, 3, 4, 5, 6]
    bar_width = 0.25

    plt.bar(shift_positions(x, -bar_width), data["UCS"][column], width=bar_width, label="UCS", color=colors["UCS"])
    plt.bar(x, data["A*"][column], width=bar_width, label="A*", color=colors["A*"])
    plt.bar(shift_positions(x, bar_width), data["Hill Climbing"][column], width=bar_width, label="Hill Climbing", color=colors["Hill Climbing"])

    plt.xticks(x, get_labels(games))

def shift_positions(positions, amount): # adds small number to ever item
    moved = [] # init array for moved
    for p in positions: # for each position, we add the amount and append to moved
        moved.append(p + amount)
    return moved

# --------------------------------------------------------------------------------
# actual plotting of results, functions for building bar charts for each metric  |
# -------------------------------------------------------------------------------- 
def plot_bars(games, data, column, ylabel, title, filename, use_log): # plot bars depending on column, ylabel, title, filename, use_log
    # column is our point of comparison
    plt.figure(figsize=(10, 5)) 
    draw_three_bars(games, data, column)

    if use_log:
        plt.yscale("log")

    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


games, summary = read_results("results.csv") # read results.csv and store the data in games and data variables
raw_data = read_all("raw_results.csv") # read raw_results.csv and store the data in raw_data variable
map_areas = get_dimensions(raw_data)

# calls plotting functions
plot_bars(games, summary, "success_rate", "Success Rate (%)", "Success Rate per Game", "charts/success_rate.png", False)
plot_bars(games, summary, "avg_nodes_expanded", "Avg Nodes Expanded (log)", "Average Nodes Expanded per Game", "charts/average_nodes.png", True)
plot_bars(games, summary, "avg_runtime_s", "Avg Runtime in seconds (log)", "Average Runtime per Game", "charts/average_runtime.png", True)