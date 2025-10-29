import requests
import os

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_commute_data(origin, destination, mode="driving"):
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": f"{origin['lat']},{origin['lng']}",
        "destinations": f"{destination['lat']},{destination['lng']}",
        "mode": mode,
        "key": GOOGLE_MAPS_API_KEY
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        element = data["rows"][0]["elements"][0]
        if element.get("status") != "OK":
            raise ValueError(f"Route error: {element.get('status')}")

        distance_km = element["distance"]["value"] / 1000
        duration_min = element["duration"]["value"] / 60

        return {
            "distance_km": round(distance_km, 2),
            "time_min": round(duration_min, 1)
        }

    except Exception as e:
        return {"error": str(e)}


def compute_relocation_cost(origin, destination, volume_cubic_meters, fragile=False, extra_services=None):
    if extra_services is None:
        extra_services = []

    distance_km = 845.32
    distance_cost = distance_km * 15
    handling_cost = 12000
    fragile_multiplier = 1.2 if fragile else 1.0
    extras = 2000 if extra_services else 0

    subtotal = (distance_cost + handling_cost + extras) * fragile_multiplier
    tax = subtotal * 0.18
    total = subtotal + tax

    return {
        "distance_km": round(distance_km, 2),
        "distance_cost": round(distance_cost, 2),
        "handling_cost": handling_cost,
        "fragile_multiplier": fragile_multiplier,
        "extras": extras,
        "tax": round(tax, 2),
        "total": round(total, 2),
        "currency": "INR"
    }
