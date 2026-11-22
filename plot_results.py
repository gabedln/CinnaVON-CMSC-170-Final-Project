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

 # function for plotting frontier vs total nodes, to show that A* stores far fewer nodes than UCS
def plot_frontier_vs_total(games, data, filename):
    plt.figure(figsize=(13, 5))
    x = list(range(len(games)))
  
    # this function prints 2 graphs together; one for peak open list, and one for total nodes (closed + peak open)
    plt.subplot(1, 2, 1)
    draw_three_bars(games, data, "avg_peak_open")
    plt.ylabel("Avg Peak Open List Size") # for hill climbing, always 0 since it doesn't store any nodes
    plt.title("Frontier Queue Only (A* > UCS)") # average peak open list only
    plt.legend() # plot legend
    plt.grid(axis="y", alpha=0.3) # plot grid

    # second graph, one for total nodes
    plt.subplot(1, 2, 2) # plt.subplot(nrows, ncols, index) creates a subplot in a grid of nrows x ncols, at position index
    ucs_total = [] # list to store total nodes for UCS
    astar_total = [] # list to store total nodes for A*
    for i in x: # for each game, we compute the total nodes (closed + peak open) for UCS and A* and append to the respective lists
        ucs_total.append(data["UCS"]["avg_nodes_expanded"][i] + data["UCS"]["avg_peak_open"][i])
        astar_total.append(data["A*"]["avg_nodes_expanded"][i] + data["A*"]["avg_peak_open"][i])

    bar_width = 0.35
    plt.bar(shift_positions(x, -0.175), ucs_total, width=bar_width, label="UCS", color=colors["UCS"])
    plt.bar(shift_positions(x, 0.175), astar_total, width=bar_width, label="A*", color=colors["A*"])

    plt.yscale("log") # node footprint is usually large, so we use log scale to make it more readable
    plt.xticks(x, get_labels(games)) # xticks are the game names, we use get_labels to get the short names for the games
    plt.ylabel("Closed + Peak Open (log scale)")
    plt.title("Total Node Footprint (A* Stores Far Fewer)")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def plot_speedup_and_reduction(games, data, filename):
    plt.figure(figsize=(13, 5))

    # Count downward [6, 5, 4, 3, 2, 1, 0] so the first game sits at the top of the chart
    y = list(range(len(games) - 1, -1, -1))
    labels = []
    for name in get_labels(games):
        labels.append(name.replace("\n", " "))

    speedups = []
    node_red = []
    time_red = []
    for i in range(len(games)):
        u_t = data["UCS"]["avg_runtime_s"][i]
        a_t = data["A*"]["avg_runtime_s"][i]
        u_n = data["UCS"]["avg_nodes_expanded"][i]
        a_n = data["A*"]["avg_nodes_expanded"][i]
        speedups.append(u_t / a_t)
        node_red.append((1 - a_n / u_n) * 100)
        time_red.append((1 - a_t / u_t) * 100)

    # Left graph: Horizontal bar chart for A* speedup
    plt.subplot(1, 2, 1)
    plt.barh(y, speedups, color=colors["A*"])
    for i in range(len(games)):
        plt.text(speedups[i] + 0.06, y[i], str(round(speedups[i], 2)) + "x", va="center")
    plt.axvline(1.0, color=colors["UCS"], linestyle="--", label="UCS baseline (1.0x)")
    plt.yticks(y, labels)
    plt.xlim(0, max(speedups) + 0.7)
    plt.xlabel("Speedup (UCS runtime / A* runtime)")
    plt.title("A* Speedup Over UCS (Horizontal Bars)")
    plt.legend()
    plt.grid(axis="x", alpha=0.3)

    # Right graph: Grouped horizontal bar chart for Node % vs Runtime % saved
    plt.subplot(1, 2, 2)
    bar_height = 0.35
    y_top = shift_positions(y, bar_height / 2)
    y_bot = shift_positions(y, -bar_height / 2)

    plt.barh(y_top, node_red, height=bar_height, color=colors["UCS"], label="Node Reduction %")
    plt.barh(y_bot, time_red, height=bar_height, color=colors["Hill Climbing"], label="Runtime Reduction %")

    for i in range(len(games)):
        plt.text(node_red[i] + 1.2, y_top[i], str(round(node_red[i], 1)) + "%", va="center", fontsize=8)
        plt.text(time_red[i] + 1.2, y_bot[i], str(round(time_red[i], 1)) + "%", va="center", fontsize=8)

    plt.yticks(y, labels)
    plt.xlim(0, 92)
    plt.ylim(-0.6, len(games) + 0.35)
    plt.xlabel("Reduction vs UCS (%)")
    plt.title("A* Node vs Runtime Reduction (%)")
    plt.legend(loc="upper center", ncol=2, fontsize=10)
    plt.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def get_failure_rates(values, found_flags, buckets):
    failed = [0] * len(buckets)
    total = [0] * len(buckets)

    for i in range(len(values)):
        for b in range(len(buckets)):
            low, high, _ = buckets[b]
            if low <= values[i] < high:
                total[b] += 1
                if not found_flags[i]:
                    failed[b] += 1
                break

    rates = []
    labels = []
    for b in range(len(buckets)):
        rates.append((failed[b] / total[b]) * 100)
        labels.append(buckets[b][2])
    return rates, labels

def plot_hc_failure_by_size(raw_rows, map_areas, filename):
    # Collect just the Hill Climbing rows into three simple lists
    hc_areas = []
    hc_lengths = []
    hc_found = []
    for row in raw_rows:
        if row["method"] == "Hill Climbing":
            hc_areas.append(map_areas[(row["game"], row["map"])])
            hc_lengths.append(row["optimal"])
            hc_found.append(row["found"])

    size_buckets = [
        (0, 5000, "<5k\ncells"),
        (5000, 25000, "5k-25k\ncells"),
        (25000, 100000, "25k-100k\ncells"),
        (100000, 270000, "100k-270k\n(512x512)"),
        (270000, 9999999, "270k+\n(SC1/Large)"),
    ]
    len_buckets = [
        (0, 50, "0-50"),
        (50, 150, "50-150"),
        (150, 300, "150-300"),
        (300, 600, "300-600"),
        (600, 1000, "600-1000"),
        (1000, 999999, "1000+"),
    ]

    s_rates, s_labels = get_failure_rates(hc_areas, hc_found, size_buckets)
    l_rates, l_labels = get_failure_rates(hc_lengths, hc_found, len_buckets)

    plt.figure(figsize=(13, 5))

    # Left graph: Failure Rate vs Map Size (line graph)
    plt.subplot(1, 2, 1)
    sx = list(range(len(s_rates)))
    plt.plot(sx, s_rates, marker="o", linewidth=2.5, color=colors["UCS"])
    plt.fill_between(sx, s_rates, alpha=0.2, color=colors["Hill Climbing"])
    for b in sx:
        plt.text(b, s_rates[b] + 2.5, str(round(s_rates[b], 1)) + "%", ha="center")
    plt.xticks(sx, s_labels)
    plt.ylim(0, 108)
    plt.xlabel("Map Grid Size (width × height)")
    plt.ylabel("Hill Climbing Failure Rate (%)")
    plt.title("Hill Climbing Failure Rate vs Map Size")
    plt.grid(True, alpha=0.3)

    # Right graph: Failure Rate vs Path Length (bar graph)
    plt.subplot(1, 2, 2)
    lx = list(range(len(l_rates)))
    plt.bar(lx, l_rates, width=0.55, color=colors["A*"])
    for b in lx:
        plt.text(b, l_rates[b] + 1.8, str(round(l_rates[b], 1)) + "%", ha="center")
    plt.xticks(lx, l_labels)
    plt.ylim(0, 108)
    plt.xlabel("Optimal Path Length")
    plt.ylabel("Hill Climbing Failure Rate (%)")
    plt.title("Hill Climbing Failure Rate vs Path Length")
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
plot_frontier_vs_total(games, summary, "charts/frontier_total.png")
plot_speedup_and_reduction(games, summary, "charts/speedup_reduction.png")
plot_hc_failure_by_size(raw_data, map_areas, "charts/hc_failure_by_size.png")