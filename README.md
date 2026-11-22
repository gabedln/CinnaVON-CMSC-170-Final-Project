# CinnaVON-CMSC-170-Final-Project

# Evaluating Completeness, Optimality, and Efficiency Across UCS, A* Search, and Steepest-Descent Hill Climbing on 2D Video Game Pathfinding Benchmarks


The goal of this project is to observe the differences of uninformed, informed, and local search using a standardized benchmark like the 2D video game maps used as the dataset in this project. The link to the dataset can be found here:
[DataSet](https://www.movingai.com/benchmarks/grids.html)

To run the code, ensure python is installed and run main.py:

Linux & macOS:

`python3 main.py`

Windows:

`python main.py` or `py main.py`

Evaluation Metrics:

| Metric | Explanation |
| --- | --- |
| Success | How often the method was able to reach the goal |
| Optimal | How often the method was able to find the optimal route to reach the goal |
| Cost ratio | How close the found route was to the optimal route on successful runs |
| Avg nodes | Average number of states popped from the open list before reaching the goal or giving up |
| Avg peak open | The maximum number of candidates stored in the open list at any point during a search, averaged across all scenarios |
| Avg runtime (s) | Average runtime for each method, averaged across all scenarios, recorded in seconds |

The only metric that could differ across different runs or devices is avg runtime which could vary due to CPU differences. Other metrics should remain the same.