'''
Steepest descent hill climbing: evaluate all neighbors and move to the one offering the best improvement.
Simple hill climbing moves to the first neighbor that has an improvement.
This is a heuristic greedy local search optimization algorithm, and it is called steepest descent because
it looks for the lowest values, since it is trying to find the shortest distance on a map.
'''

import math
import time  # for measuring the runtime

from a_ucs import (
    TOLERANCE,  # same allowed rounding difference when checking optimality
    get_neighbors,  # same movement rules as UCS and A* (no corner cutting)
    is_passable,  # same terrain passability check as UCS and A* (handles W, @, O, T)
)


# Heuristic function for estimating distance in octile grid
def octile_distance(x1, y1, x2, y2):
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy) # Cardinal cost = 1, Diagonal cost = sqrt(2)


def hill_climbing(map_data, height, width, start_x, start_y, goal_x, goal_y):
    start = (start_x, start_y)
    goal = (goal_x, goal_y)

    # Bounds and terrain validation
    if not is_passable(map_data, width, height, start_x, start_y) or not is_passable(map_data, width, height, goal_x, goal_y):
        return None, float('inf'), 0

    if start == goal:
        return [start], 0.0, 0

    current = start
    current_h = octile_distance(start_x, start_y, goal_x, goal_y)
    path = [current]
    total_cost = 0.0
    visited = {current}
    nodes_expanded = 0 # how many cells hill climbing looked around from

    while current != goal:
        nodes_expanded += 1 # looking at the neighbors of current, so it counts as expanded
        neighbors = get_neighbors(map_data, width, height, current[0], current[1])

        best_neighbor = None
        best_move_cost = 0.0
        best_h = float('inf')

        # Evaluate all valid neighbors and select the one closest to the goal
        for next_node, move_cost in neighbors:
            if next_node in visited:
                continue

            h = octile_distance(next_node[0], next_node[1], goal_x, goal_y)
            if h < best_h:
                best_h = h
                best_neighbor = next_node
                best_move_cost = move_cost

        # Done if no neighbor offers an improvement (local minimum)
        if best_neighbor is None or best_h >= current_h:
            return None, float('inf'), nodes_expanded

        current = best_neighbor
        current_h = best_h
        visited.add(current)
        path.append(current)
        total_cost += best_move_cost

    return path, total_cost, nodes_expanded


# RUNNING HILL CLIMBING ON ONE SCENARIO AND TIMING IT (same output format as run_one in a_ucs.py)
def run_hill_climbing(grid, width, height, scenario):
    _bucket, start, goal, optimal = scenario
    start_time = time.time()
    path, cost, nodes_expanded = hill_climbing(grid, height, width, start[0], start[1], goal[0], goal[1])
    runtime = time.time() - start_time # in seconds

    peak_open = 1 # hill climbing has no open list, it only keeps the current cell

    if path is None:
        return [False, 0, nodes_expanded, peak_open, runtime, False]

    difference = cost - optimal
    if difference < 0:
        difference = -difference # |cost - optimal|
    is_optimal = difference < TOLERANCE # same as the .scen optimal length?
    return [True, cost, nodes_expanded, peak_open, runtime, is_optimal]
