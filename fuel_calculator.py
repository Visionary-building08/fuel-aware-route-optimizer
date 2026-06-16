"""
Fuel cost calculator.
Computes estimated fuel usage and cost, with traffic and road quality adjustments.
"""

FUEL_PRICE_PER_LITRE = 100.0  # ₹ per litre (assumed constant)


def calculate_fuel_cost(
    distance_km: float,
    mileage_kmpl: float,
    traffic_multiplier: float = 1.0,
    road_quality_multiplier: float = 1.0,
) -> dict:
    """
    Estimate fuel cost for a given segment.

    Args:
        distance_km: distance of the segment in km
        mileage_kmpl: vehicle fuel efficiency in km/litre
        traffic_multiplier: penalty from traffic model (1.0 = no penalty)
        road_quality_multiplier: penalty from road quality model (1.0 = no penalty)

    Returns:
        dict with fuel_litres, base_cost, adjusted_cost
    """
    # Base fuel usage
    fuel_litres = distance_km / mileage_kmpl

    # Base cost before any penalties
    base_cost = fuel_litres * FUEL_PRICE_PER_LITRE

    # Combined penalty: traffic affects time/consumption; road quality affects wear/cost
    # We apply road quality to cost and traffic adds indirect fuel increase
    adjusted_cost = base_cost * road_quality_multiplier * traffic_multiplier

    return {
        "fuel_litres": round(fuel_litres, 3),
        "base_cost": round(base_cost, 2),
        "adjusted_cost": round(adjusted_cost, 2),
    }


def total_fuel_cost(segment_costs: list) -> float:
    """Sum adjusted costs across all segments."""
    return round(sum(s["adjusted_cost"] for s in segment_costs), 2)
