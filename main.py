from load_map import read_map, read_scen, pick_scenarios
from a_ucs import run_one, zero_heuristic, octile_distance
from hill_climbing import run_hill_climbing
from metrics import success_rate, optimality_rate, avg_cost_ratio, average

MAPS = ["lak110d", "arena", "den312d", "ost003d", "den520d", "brc505d", "orz103d"] # dragon age: origins maps, small to large
METHODS = ["UCS", "A*", "Hill Climbing"]


# PRINTING A LINE ON THE CONSOLE AND WRITING IT ON THE OUTPUT FILE
def show(line, out_file):
    print(line)
    out_file.write(line + "\n")


# RUNNING ONE METHOD ON ONE SCENARIO
def run_method(method, grid, width, height, scenario):
    if method == "UCS":
        return run_one(grid, width, height, scenario, zero_heuristic) # h = 0
    if method == "A*":
        return run_one(grid, width, height, scenario, octile_distance) # h = octile
    return run_hill_climbing(grid, width, height, scenario)


# ONE ROW OF THE TABLE FOR ONE METHOD, USING THE FUNCTIONS FROM metrics.py
def table_row(method, results, scenarios):
    name = method
    if len(name) < 8:
        name = name + "\t" # extra tab so the short names line up with "Hill Climbing"
    return (name + "\t"
            + str(round(success_rate(results), 2)) + "%\t\t"
            + str(round(optimality_rate(results), 2)) + "%\t\t"
            + str(round(avg_cost_ratio(results, scenarios), 4)) + "\t\t"
            + str(round(average(results, 2), 2)) + "\t\t"
            + str(round(average(results, 3), 2)) + "\t\t"
            + str(round(average(results, 4), 6)))


# MAIN FUNCTION
def main():
    sample_size = int(input("how many scenarios to test per map? ").strip())
    while sample_size <= 0:
        sample_size = int(input("should be more than 0. enter again: ").strip())

    out_file = open("output.txt", "w") # the tables
    csv_file = open("results.csv", "w") # every single run, for the graphs
    csv_file.write("map,method,found,cost,optimal,nodes_expanded,peak_open,runtime,is_optimal\n")

    print()
    show("UCS vs A* (octile) vs Hill Climbing on Moving AI 2D Pathfinding Benchmarks", out_file)
    show("Group CinnaVON", out_file)
    show("", out_file)
    show("Scenarios per map: " + str(sample_size) + " (evenly spread from easiest to hardest)", out_file)
    show("", out_file)

    # all_results[method] = results of that method from every map, all_scenarios = the matching scenarios
    all_results = {}
    for method in METHODS:
        all_results[method] = []
    all_scenarios = []

    for name in MAPS:
        height, width, grid = read_map("dao-map/" + name + ".map")
        scenarios = read_scen("dao-scen/" + name + ".map.scen")
        chosen = pick_scenarios(scenarios, sample_size)

        show("Map: " + name + " (" + str(width) + "x" + str(height) + ")", out_file)
        show("Method\t\tSuccess\t\tOptimal\t\tCost ratio\tAvg nodes\tAvg peak open\tAvg runtime (s)", out_file)

        for method in METHODS:
            results = []
            for scenario in chosen:
                result = run_method(method, grid, width, height, scenario)
                results.append(result)
                all_results[method].append(result)

                # one line in the csv per run: map, method, then the result values
                found, cost, nodes, peak, runtime, is_optimal = result
                csv_file.write(name + "," + method + "," + str(found) + "," + str(cost) + "," + str(scenario[3]) + ","
                               + str(nodes) + "," + str(peak) + "," + str(runtime) + "," + str(is_optimal) + "\n")

            show(table_row(method, results, chosen), out_file)

        for scenario in chosen:
            all_scenarios.append(scenario)
        show("", out_file)

    show("-------------------------------------------------", out_file)
    show("OVERALL (" + str(len(all_scenarios)) + " scenarios, " + str(len(MAPS)) + " maps)", out_file)
    show("Method\t\tSuccess\t\tOptimal\t\tCost ratio\tAvg nodes\tAvg peak open\tAvg runtime (s)", out_file)
    for method in METHODS:
        show(table_row(method, all_results[method], all_scenarios), out_file)
    show("", out_file)
    show("cost ratio = path cost / optimal length, solved scenarios only (1.0 = optimal)", out_file)

    out_file.close() # close after writing
    csv_file.close()
    print("yey! check output.txt for the tables and results.csv for the raw data :)")


main()