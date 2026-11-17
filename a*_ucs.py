import heapq # priority queue, so we always get the node with the lowest f(n) first
import time # for measuring the runtime of each search

TOLERANCE = 0.001 # allowed difference from the optimal length because of float rounding
DIAGONAL_COST = 2 ** (1 / 2) # sqrt(2), cost of moving diagonally, straight moves cost 1
PASSABLE = ".GS" # chars that can be walked on, everything else is blocked


# ===========================================================================================
# Section for Heuristics:                                                                   |
# Explanation: UCS uses a zero heuristic, while A* uses the octile distance heuristic.      |
# ===========================================================================================

# zero heuristic (for UCS)
def zero_heuristic(start, goal):
    return 0
# octile distance heuristic (for A*)
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

# ===========================================================================================
# The actual search logic in the function                                                   |
# The only difference is the heuristic used (zero for UCS, octile for A*)                   |
# ===========================================================================================

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
