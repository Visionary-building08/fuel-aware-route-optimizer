"""
Route Optimizer — core business logic.
Orchestrates: Geocoding → OSRM routing → TSP → traffic/road adjustments → fuel cost.
"""

from typing import List
from services.maps_service import MapsService
from services.traffic_model import apply_traffic_penalty, get_traffic_multiplier
from services.road_quality_model import load_road_quality_map, get_location_cost_multiplier
from core.tsp_solver import nearest_neighbor_tsp
from core.fuel_calculator import calculate_fuel_cost, total_fuel_cost


class RouteOptimizer:
    def __init__(self, api_key: str = None):
        self.maps = MapsService(api_key)
        self.road_quality_map = load_road_quality_map()

    def optimize(
        self,
        start: str,
        stops: List[str],
        time_of_day: str,
        mileage_kmpl: float,
    ) -> dict:
        all_locations = [start] + stops

        # Step 1: Get distance/duration matrices + coords for map display
        dist_matrix, dur_matrix, coords = self.maps.build_distance_duration_matrix(all_locations)

        # Step 2: TSP — find optimal visit order
        route_indices, _ = nearest_neighbor_tsp(dist_matrix, start_index=0)
        ordered_locations = [all_locations[i] for i in route_indices]
        ordered_coords = [coords[i] for i in route_indices]

        # Step 3: Compute per-segment metrics
        traffic_mult = get_traffic_multiplier(time_of_day)
        segments = []
        total_distance = 0.0
        total_duration_sec = 0.0

        for k in range(len(route_indices) - 1):
            i = route_indices[k]
            j = route_indices[k + 1]

            seg_dist = dist_matrix[i][j]
            seg_dur_adjusted = apply_traffic_penalty(dur_matrix[i][j], time_of_day)
            dest_name = all_locations[j]
            road_mult = get_location_cost_multiplier(dest_name, self.road_quality_map)
            cost_info = calculate_fuel_cost(seg_dist, mileage_kmpl, traffic_mult, road_mult)

            segments.append({
                "from": all_locations[i],
                "to": dest_name,
                "distance_km": round(seg_dist, 2),
                "duration_min": round(seg_dur_adjusted / 60, 1),
                "fuel_litres": cost_info["fuel_litres"],
                "adjusted_cost": cost_info["adjusted_cost"],
            })

            total_distance += seg_dist
            total_duration_sec += seg_dur_adjusted

        return {
            "ordered_route": ordered_locations,
            "ordered_coords": ordered_coords,   # (lat, lng) list for map
            "segments": segments,
            "total_distance_km": round(total_distance, 2),
            "total_duration_min": round(total_duration_sec / 60, 1),
            "total_fuel_cost_inr": total_fuel_cost(segments),
            "total_fuel_litres": round(sum(s["fuel_litres"] for s in segments), 3),
        }
