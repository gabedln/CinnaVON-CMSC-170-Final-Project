import csv
import os

from a_ucs import octile_distance, run_one, zero_heuristic
from hill_climbing import run_hill_climbing
from load_map import list_maps, pick_scenarios, read_map, read_scen
from metrics import average, avg_cost_ratio, optimality_rate, success_rate

# All 6 Moving AI commercial game benchmark suites (5 unique games; Baldur's Gate II has original and 512x512 scaled sets)
GAMES = [
    ("Baldur's Gate II (Original)", "bgmaps-map", "bgmaps-scen"),
    ("Baldur's Gate II (512x512)", "bg512-map", "bg512-scen"),
    ("Dragon Age: Origins", "dao-map", "dao-scen"),
    ("Dragon Age II", "da2-map", "da2-scen"),
    ("StarCraft", "sc1-map", "sc1-scen"),
    ("Warcraft III (512x512)", "wc3maps512-map", "wc3maps512-scen"),
]
METHODS = ["UCS", "A*", "Hill Climbing"]


# PRINTING A LINE ON THE CONSOLE AND WRITING IT ON THE OUTPUT FILE
def show(line, out_file): # prints a line on the console and writes it on the output file
    print(line)
    out_file.write(line + "\n")


# RUNNING ONE METHOD ON ONE SCENARIO
def run_method(method, grid, width, height, scenario):
    if method == "UCS":
        return run_one(grid, width, height, scenario, zero_heuristic) # h = 0
    if method == "A*":
        return run_one(grid, width, height, scenario, octile_distance) # h = octile
    return run_hill_climbing(grid, width, height, scenario)


# COMPUTING SUMMARY METRICS FOR ONE METHOD OVER A SET OF RESULTS AND SCENARIOS
def summarize(results, scenarios): # call the functions from metrics.py to compute the summary metrics for one method over a set of results and scenarios
    if len(results) == 0:
        return 0, 0, 0, 0, 0, 0
    return (
        round(success_rate(results), 2),
        round(optimality_rate(results), 2),
        round(avg_cost_ratio(results, scenarios), 4),
        round(average(results, 2), 2),
        round(average(results, 3), 2),
        round(average(results, 4), 6),
    )


# TABLE HEADER AND FORMATTED ROW USING FIXED-WIDTH F-STRINGS SO COLUMNS ALWAYS ALIGN
TABLE_HEADER = (
    f"{'Method':<15} {'Success':>9} {'Optimal':>9} {'Cost ratio':>12} "
    f"{'Avg nodes':>12} {'Avg peak open':>15} {'Avg runtime (s)':>17}"
)

def table_row(method, summary): # formats result into a string using fixed-width f-strings so columns always align
    succ, opt, ratio, nodes, peak, runtime = summary
    return (
        f"{method:<15} {succ:>8.2f}% {opt:>8.2f}% {ratio:>12.4f} "
        f"{nodes:>12.2f} {peak:>15.2f} {runtime:>17.6f}"
    )


# MAIN FUNCTION
def main():
    sample_size = 10 # number of scenarios to run per map (evenly spaced from easiest to hardest)

    # setting up our output files for writing results, summaries, and raw data
    out_file = open("output.txt", "w", encoding="utf-8") # per-game & overall tables  # noqa: SIM115
    summary_file = open("results.csv", "w", newline="", encoding="utf-8") # per-game summaries (for charts/tables)  # noqa: SIM115
    raw_file = open("raw_results.csv", "w", newline="", encoding="utf-8") # every single scenario run  # noqa: SIM115

    # setting up our csv files for writing results, summaries, and raw data
    summary_writer = csv.writer(summary_file)
    summary_writer.writerow([
        "game", "method", "maps", "scenarios",
        "success_rate", "optimality_rate", "avg_cost_ratio",
        "avg_nodes_expanded", "avg_peak_open", "avg_runtime_s",
    ])
    # summary writer = per game, raw writer = every single scenario run (15870 total)
    raw_writer = csv.writer(raw_file)
    raw_writer.writerow([
        "game", "map", "method", "found", "cost", "optimal",
        "nodes_expanded", "peak_open", "runtime", "is_optimal",
    ])

    print()
    show("Evaluating Completeness, Optimality, and Efficiency Across UCS, A* Search, and Steepest-Descent Hill Climbing on 2D Video Game Pathfinding Benchmarks", out_file)
    show("", out_file)
    show("Benchmark suites: " + str(len(GAMES)) + " (all maps per suite)", out_file)
    show("Scenarios per map: " + str(sample_size) + " (evenly spaced from easiest to hardest)", out_file)
    show("", out_file)

    # overall accumulators across all games
    all_results = {method: [] for method in METHODS}
    all_scenarios = []
    total_maps = 0

    for game_name, map_dir, scen_dir in GAMES: # iterates for all games in game list and gets game name and dir for map and scenario files
        map_names = list_maps(map_dir, scen_dir) # gets all map names in the map dir that have a matching .scen file in the scenario dir
        total_maps += len(map_names) # accumulates total number of maps across all games

        game_results = {method: [] for method in METHODS} # similar to all_results, but only for the current game
        game_scenarios = [] # similar to all_scenarios, but only for the current game

        print(f"Running {game_name} ({len(map_names)} maps)...") # prints the current game that we are running

        for idx, name in enumerate(map_names, start=1): # loops through map names while keeping indx (counter), starts at 1
            # we use enumerate so for progress reporting (how many maps already done)
            height, width, grid = read_map(os.path.join(map_dir, name + ".map")) # we use the read map from load_map.py
            scenarios = read_scen(os.path.join(scen_dir, name + ".map.scen")) # we use read scen from load_map.py to get the scenarios for the current map
            chosen = pick_scenarios(scenarios, sample_size) # chose 10 scenarios using pick_scenarios

            for method in METHODS: # loops through all methods (UCS, A*, Hill Climbing) and runs each method on the current map and chosen scenarios
                for scenario in chosen: # for each method, we run each scenario in the chosen scenarios for the current map
                    result = run_method(method, grid, width, height, scenario) # runs the current method on the current map and scenario, returns a list of results (found, cost, nodes_expanded, peak_open, runtime, is_optimal)
                    game_results[method].append(result)
                    all_results[method].append(result)

                    found, cost, nodes, peak, runtime, is_optimal = result # gets the result
                    raw_writer.writerow([ # writes down individual scenario results to the raw_results.csv file
                        game_name, name, method, found, cost, scenario[3],
                        nodes, peak, runtime, is_optimal,
                    ])

            game_scenarios.extend(chosen) #  adds the chosen scenarios for the current map to the game_scenarios list, which will be used for summarizing results for the current game
            all_scenarios.extend(chosen) #  adds the chosen scenarios for the current map to the all_scenarios list, which will be used for summarizing results across all games

            if idx % 25 == 0 or idx == len(map_names): # for ever 25 maps, or if we are on the last map, we print the progress of how many maps have been completed for the current game
                print(f" {game_name}: {idx}/{len(map_names)} maps done")
        
        show(f"Game: {game_name} ({len(map_names)} maps, {len(game_scenarios)} scenarios)", out_file)
        show(TABLE_HEADER, out_file)

        for method in METHODS:
            summary = summarize(game_results[method], game_scenarios)
            show(table_row(method, summary), out_file)
            succ, opt, ratio, nodes, peak, runtime = summary
            summary_writer.writerow([
                game_name, method, len(map_names), len(game_scenarios),
                succ, opt, ratio, nodes, peak, runtime,
            ])

        show("", out_file)

    show("-" * len(TABLE_HEADER), out_file)
    show("OVERALL (" + str(len(all_scenarios)) + " scenarios, " + str(total_maps) + " maps, " + str(len(GAMES)) + " benchmark suites)", out_file)
    show(TABLE_HEADER, out_file)
    for method in METHODS:
        summary = summarize(all_results[method], all_scenarios)
        show(table_row(method, summary), out_file)
        succ, opt, ratio, nodes, peak, runtime = summary
        summary_writer.writerow([
            "OVERALL", method, total_maps, len(all_scenarios),
            succ, opt, ratio, nodes, peak, runtime,
        ])

    show("", out_file)

    out_file.close()
    summary_file.close()
    raw_file.close()


if __name__ == "__main__":
    main()