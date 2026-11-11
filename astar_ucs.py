import heapq # priority queue, so we always get the node with the lowest f(n) first
import time # for measuring the runtime of each search

DIAGONAL_COST = 2 ** (1 / 2) # sqrt(2), cost of moving diagonally, straight moves cost 1
PASSABLE = ".GS" # chars that can be walked on, everything else is blocked
TOLERANCE = 0.001 # allowed difference from the optimal length because of float rounding


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
    return grid, width, height


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


# CHECKING IF A CELL CAN BE WALKED ON
def is_passable(grid, width, height, x, y):
    if x < 0 or x >= width or y < 0 or y >= height:
        return False # outside the map
    return grid[y][x] in PASSABLE # grid is row by row, so y first then x


# GETTING THE 8 NEIGHBORS OF A CELL WITH THEIR MOVE COST (Actions and Result)
def get_neighbors(grid, width, height, x, y):
    neighbors = [] # each one is [(x, y), cost]
    moves = [(0, -1), (0, 1), (-1, 0), (1, 0),     # up, down, left, right
             (-1, -1), (1, -1), (-1, 1), (1, 1)]   # the 4 diagonals
    for dx, dy in moves:
        new_x = x + dx
        new_y = y + dy
        if not is_passable(grid, width, height, new_x, new_y):
            continue # blocked or outside the map

        if dx != 0 and dy != 0:
            # diagonal move, no corner cutting: both side cells beside it must be open too
            if not is_passable(grid, width, height, x + dx, y) or not is_passable(grid, width, height, x, y + dy):
                continue
            neighbors.append([(new_x, new_y), DIAGONAL_COST])
        else:
            neighbors.append([(new_x, new_y), 1])
    return neighbors


# OCTILE DISTANCE HEURISTIC (FOR A*)
def octile_distance(cell, goal):
    dx = cell[0] - goal[0]
    if dx < 0:
        dx = -dx # |x1 - x2|
    dy = cell[1] - goal[1]
    if dy < 0:
        dy = -dy # |y1 - y2|

    if dx > dy:
        bigger = dx
        smaller = dy
    else:
        bigger = dy
        smaller = dx
    # go diagonal for the smaller part, then straight for the rest
    # h = max(dx, dy) + (sqrt(2) - 1) * min(dx, dy)
    return bigger + (DIAGONAL_COST - 1) * smaller


# ZERO HEURISTIC (FOR UCS)
def zero_heuristic(cell, goal):
    return 0 # no guess at all, so f(n) = g(n), lowest path cost first = uniform cost search


# BUILDING THE PATH FROM THE GOAL BACK TO THE START
def build_path(parent, goal):
    backwards = [] # goal first, start last
    current = goal
    while current is not None:
        backwards.append(current)
        current = parent[current]

    path = [] # flip it so start comes first
    i = len(backwards) - 1
    while i >= 0:
        path.append(backwards[i])
        i -= 1
    return path


# THE SEARCH ITSELF, FOLLOWING THE A* PSEUDOCODE (A* WHEN USING OCTILE, UCS WHEN USING ZERO)
def search(grid, width, height, start, goal, heuristic):
    # openList = frontier, closedList = explored cells, bestNode = lowest f(n)
    tie_breaker = 0 # keeps nodes with equal f(n) in the order they were added
    open_list = [(heuristic(start, goal), 0, tie_breaker, start)] # openList = { initialState }, each is (f, g, tie, cell)
    closed_list = set() # closedList = { }

    best_g = {start: 0} # cheapest g(n) found so far for each cell in the openList
    parent = {start: None} # where we came from, used to rebuild the path at the end
    nodes_expanded = 0
    peak_open = 1 # biggest size the open list reached, our memory metric

    while len(open_list) > 0: # while openList is not empty
        f, g, tie, best_node = heapq.heappop(open_list) # bestNode = openList.removeMinF()

        if best_node in closed_list:
            continue # this is an old copy, a better one was already expanded (instead of delete(duplicate))

        closed_list.add(best_node) # closedList.add(bestNode)
        nodes_expanded += 1

        if best_node == goal: # if GoalTest(bestNode) return bestNode
            return build_path(parent, goal), g, nodes_expanded, peak_open

        for x, step_cost in get_neighbors(grid, width, height, best_node[0], best_node[1]): # x = Result(bestNode, a)
            if x in closed_list:
                continue # x is already in the closedList, skip it
            new_g = g + step_cost
            if x in best_g and best_g[x] <= new_g:
                continue # x is in the openList and its duplicate is already equal or better
            best_g[x] = new_g # x is new, or better than its duplicate
            parent[x] = best_node
            tie_breaker += 1
            new_f = new_g + heuristic(x, goal) # f(n) = g(n) + h(n)
            heapq.heappush(open_list, (new_f, new_g, tie_breaker, x)) # openList.add(x)

        if len(open_list) > peak_open:
            peak_open = len(open_list)

    return None, None, nodes_expanded, peak_open # no path found


# RUNNING ONE METHOD ON ONE SCENARIO AND TIMING IT
def run_one(grid, width, height, scenario, heuristic):
    bucket, start, goal, optimal = scenario
    start_time = time.time()
    path, cost, nodes_expanded, peak_open = search(grid, width, height, start, goal, heuristic)
    runtime = time.time() - start_time # in seconds

    if path is None:
        return [False, 0, nodes_expanded, peak_open, runtime, False]

    difference = cost - optimal
    if difference < 0:
        difference = -difference # |cost - optimal|
    is_optimal = difference < TOLERANCE # same as the .scen optimal length?
    return [True, cost, nodes_expanded, peak_open, runtime, is_optimal]


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


# PRINTING A LINE ON THE CONSOLE AND WRITING IT ON THE OUTPUT FILE
def show(line, out_file):
    print(line)
    out_file.write(line + "\n")


# PRINTING THE SUMMARY OF ONE METHOD
def show_summary(name, results, out_file):
    solved = 0
    optimal_count = 0
    total_nodes = 0
    total_peak = 0
    total_time = 0
    for found, cost, nodes, peak, runtime, is_optimal in results:
        if found:
            solved += 1
        if is_optimal:
            optimal_count += 1
        total_nodes += nodes
        total_peak += peak
        total_time += runtime

    count = len(results)
    show(name, out_file)
    show("Solved: " + str(solved) + "/" + str(count) + " (" + str(round(solved / count * 100, 2)) + "%)", out_file)
    show("Matched optimal length: " + str(optimal_count) + "/" + str(count), out_file)
    show("Avg nodes expanded: " + str(round(total_nodes / count, 2)), out_file)
    show("Avg peak open list size: " + str(round(total_peak / count, 2)), out_file)
    show("Avg runtime (s): " + str(round(total_time / count, 6)), out_file)
    show("", out_file)


# MAIN FUNCTION
def main():
    map_file = input("enter the .map file (e.g. maps/arena.map): ").strip()
    scen_file = input("enter the .scen file (e.g. scen/arena.map.scen): ").strip()
    sample_size = int(input("how many scenarios to test? ").strip())
    while sample_size <= 0:
        sample_size = int(input("should be more than 0. enter again: ").strip())

    grid, width, height = read_map(map_file)
    scenarios = read_scen(scen_file)
    chosen = pick_scenarios(scenarios, sample_size)

    out_file = open("output.txt", "w") # opens the output.txt file in write mode

    print()
    show("UCS vs A* (octile) on Moving AI 2D Pathfinding Benchmarks", out_file)
    show("Group CinnaVON", out_file)
    show("", out_file)
    show("Map: " + map_file + " (" + str(width) + "x" + str(height) + ")", out_file)
    show("Scenarios tested: " + str(len(chosen)) + " out of " + str(len(scenarios)) + " (evenly spread)", out_file)
    show("", out_file)
    show("Bucket\tStart\t\tGoal\t\tOptimal\t\tUCS cost\tUCS nodes\tA* cost\t\tA* nodes", out_file)

    ucs_results = []
    astar_results = []
    for scenario in chosen:
        ucs = run_one(grid, width, height, scenario, zero_heuristic)
        astar = run_one(grid, width, height, scenario, octile_distance)
        ucs_results.append(ucs)
        astar_results.append(astar)

        bucket, start, goal, optimal = scenario
        show(str(bucket) + "\t" + str(start) + "\t" + str(goal) + "\t" + str(round(optimal, 4)) + "\t\t"
             + str(round(ucs[1], 4)) + "\t\t" + str(ucs[2]) + "\t\t"
             + str(round(astar[1], 4)) + "\t\t" + str(astar[2]), out_file)

    show("-------------------------------------------------", out_file)
    show_summary("UCS", ucs_results, out_file)
    show_summary("A* (octile distance)", astar_results, out_file)

    out_file.close() # close after writing
    print("yey! check the output.txt for the results :)")


main()