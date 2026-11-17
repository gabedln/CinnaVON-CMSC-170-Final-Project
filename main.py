from load_map import read_map, read_scen, pick_scenarios
from a_ucs import run_one, zero_heuristic, octile_distance

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

    height, width, grid = read_map(map_file)
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