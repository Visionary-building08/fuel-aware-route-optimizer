"""
Traveling Salesman Problem (TSP) solver.
Uses the nearest-neighbor greedy heuristic:
  - Start at index 0 (the user's start location)
  - Always visit the closest unvisited stop next
This gives a fast, good-enough solution for 3–6 stops.
"""

from typing import List, Tuple


def nearest_neighbor_tsp(
    distance_matrix: List[List[float]],
    start_index: int = 0,
) -> Tuple[List[int], float]:
    """
    Greedy nearest-neighbor TSP.
    Args:
        distance_matrix: NxN matrix of distances between all locations
        start_index: index of the starting location (always 0)
    Returns:
        (ordered_indices, total_distance)
        ordered_indices: visit order as list of location indices
    """
    n = len(distance_matrix)
    visited = [False] * n
    route = [start_index]
    visited[start_index] = True
    total_distance = 0.0

    current = start_index
    for _ in range(n - 1):
        # Find nearest unvisited neighbor
        nearest, nearest_dist = -1, float("inf")
        for j in range(n):
            if not visited[j] and distance_matrix[current][j] < nearest_dist:
                nearest = j
                nearest_dist = distance_matrix[current][j]

        if nearest == -1:
            break  # All visited

        route.append(nearest)
        visited[nearest] = True
        total_distance += nearest_dist
        current = nearest

    return route, total_distance
