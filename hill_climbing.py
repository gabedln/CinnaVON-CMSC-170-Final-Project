'''
Steepest descent hill climbing: evaluate all neighbors and move to the one offering the best improvement.
Simple hill climbing moves to the first neighbor that has an improvement.
This is a heuristic greedy local search optimization algorithm, and it is called steepest descent because
it looks for the lowest values, since it is trying to find the shortest distance on a map.
'''

import importlib
import math
from load_map import read_map as load_map

# Heuristic function for estimating distance in octile grid
def octile_distance(x1, y1, x2, y2):
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy) # Cardinal cost = 1, Diagonal cost = sqrt(2)


# Returns valid neighbors and transition costs
def get_neighbors(x, y, width, height, map_data):
    neighbors = []
    directions = [
        (0, -1, 1.0), (0, 1, 1.0), (-1, 0, 1.0), (1, 0, 1.0), # Cardinal
        (-1, -1, math.sqrt(2)), (1, -1, math.sqrt(2)), # Diagonal
        (-1, 1, math.sqrt(2)), (1, 1, math.sqrt(2)) # Diagonal
    ]

    current_char = map_data[y][x]

    for dx, dy, move_cost in directions:
        nx, ny = x + dx, y + dy

        if 0 <= nx < width and 0 <= ny < height:
            next_char = map_data[ny][nx]

            # 1. Unpassable terrain
            if next_char in ('@', 'O', 'T'):
                continue

            # 2. Water: not passable from terrain, traversable only if already in water
            if next_char == 'W' and current_char != 'W':
                continue

            # 3. Swamp: passable from regular terrain + swamp
            if next_char == 'S' and current_char not in ('.', 'G', 'S'):
                continue

            neighbors.append(((nx, ny), move_cost))

    return neighbors


def hill_climbing(map_data, height, width, start_x, start_y, goal_x, goal_y):
    start = (start_x, start_y)
    goal = (goal_x, goal_y)

    # Bounds and terrain validation
    if not (0 <= start_x < width and 0 <= start_y < height) or not (0 <= goal_x < width and 0 <= goal_y < height):
        return None, float('inf')

    if map_data[start_y][start_x] in ('@', 'O', 'T') or map_data[goal_y][goal_x] in ('@', 'O', 'T'):
        return None, float('inf')

    if start == goal:
        return [start], 0.0

    current = start
    current_h = octile_distance(start_x, start_y, goal_x, goal_y)
    path = [current]
    total_cost = 0.0
    visited = {current}

    while current != goal:
        neighbors = get_neighbors(current[0], current[1], width, height, map_data)

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
            return None, float('inf')

        current = best_neighbor
        current_h = best_h
        visited.add(current)
        path.append(current)
        total_cost += best_move_cost

    return path, total_cost


if __name__ == "__main__":
    coordinates = input("Enter start and goal coordinates separated by whitespaces in this order: \n<start x> <start y> <goal x> <goal y>: ")
    coordinates = coordinates.split()
    for index, item in enumerate(coordinates):
        coordinates[index] = int(item)

    mapdets = load_map("dao-map/arena.map")

    results = hill_climbing(mapdets[2], mapdets[0], mapdets[1], coordinates[0], coordinates[1], coordinates[2], coordinates[3])

    print(results)
