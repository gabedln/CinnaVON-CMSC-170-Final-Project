# Evaluating Completeness, Optimality, and Efficiency Across UCS, A* Search, and Steepest-Descent Hill Climbing on 2D Video Game Pathfinding Benchmarks

___

Pathfinding, defined as the problem of finding the shortest path from source to destination while avoiding obstacles (Barnouti et al. 2016). Pathfinding is a classical problem in artificial intelligence, robotics, and video-games. On a 2D map each tile acts as a node and a valid movement counts as an edge, where straight moves cost 1 and diagonal moves cost √2. Because of this, in order to find the optimal path we need to implement a weighted graph search rather than unweighted traversal. While there have been theoretical properties of search algorithms that are established in literature, this project aims to explain how differently these algorithms perform on real game maps of different sizes filled with obstacles. This project investigates the difference between three distinct search paradigms on 2D grid pathfinding. The link to the dataset can be found here:
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
