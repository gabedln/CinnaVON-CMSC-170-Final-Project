# Section for Evaluation Metrics:
# Each result is [found, cost, nodes_expanded, peak_open, runtime, is_optimal]
# and comes from run_one (UCS, A*) or run_hill_climbing (Hill Climbing)


# SUCCESS RATE: percentage of scenarios where a path was found
def success_rate(results):
    solved = 0
    for found, cost, nodes, peak, runtime, is_optimal in results:
        if found:
            solved += 1
    return solved / len(results) * 100


# OPTIMALITY RATE: percentage of scenarios where the path cost matched the .scen optimal length
def optimality_rate(results):
    optimal_count = 0
    for found, cost, nodes, peak, runtime, is_optimal in results:
        if is_optimal:
            optimal_count += 1
    return optimal_count / len(results) * 100


# COST RATIO: path cost / optimal length, averaged over solved scenarios only (1.0 = perfect)
def avg_cost_ratio(results, scenarios):
    total = 0
    solved = 0
    for i in range(len(results)):
        found = results[i][0]
        cost = results[i][1]
        optimal = scenarios[i][3]
        if found and optimal > 0:
            total += cost / optimal
            solved += 1
    if solved == 0:
        return 0 # nothing solved, so there's no ratio to compute
    return total / solved


# AVERAGE OF ONE COLUMN: 2 = nodes expanded, 3 = peak open list, 4 = runtime
def average(results, column):
    total = 0
    for result in results:
        total += result[column]
    return total / len(results)