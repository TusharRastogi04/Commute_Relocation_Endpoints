import os
import requests
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Load environment variables
load_dotenv()
ORS_API_KEY = os.getenv("ORS_API_KEY")
ORS_BASE_URL = "https://api.openrouteservice.org"

if not ORS_API_KEY:
    raise ValueError(" ORS_API_KEY is missing in your .env file.")


# ------------------------------------------------------------
# 🚗 COMMUTE INSIGHTS API VIEW
# ------------------------------------------------------------

class CommuteInsightsAPIView(APIView):
    """
    Calculates distance, duration, and estimated fuel cost between two locations (in CAD),
    with automatic fallback for long distances.
    """

    def post(self, request):
        try:
            import math

            home_address = request.data.get("home_address")
            job_address = request.data.get("job_address")
            mode = request.data.get("mode", "driving").lower()

            if not home_address or not job_address:
                return Response(
                    {"error": "Both 'home_address' and 'job_address' are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Normalize mode
            profile_map = {
                "driving": "driving-car",
                "cycling": "cycling-regular",
                "walking": "foot-walking",
            }
            mode_profile = profile_map.get(mode)
            if not mode_profile:
                return Response({"error": "Invalid mode. Use driving, cycling, or walking."},
                                status=status.HTTP_400_BAD_REQUEST)

            # ---------- GEOCODING ----------
            def geocode(address):
                ors_url = f"https://api.openrouteservice.org/geocode/search?api_key={ORS_API_KEY}&text={address}"
                ors_res = requests.get(ors_url)
                if ors_res.status_code == 200:
                    data = ors_res.json()
                    if data.get("features"):
                        coords = data["features"][0]["geometry"]["coordinates"]
                        return coords[0], coords[1]
                # fallback
                nom_url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
                nom_res = requests.get(nom_url, headers={"User-Agent": "CommuteApp/1.0"})
                if nom_res.status_code == 200 and nom_res.json():
                    j = nom_res.json()[0]
                    return float(j["lon"]), float(j["lat"])
                return None

            home_coords = geocode(home_address)
            job_coords = geocode(job_address)
            if not home_coords or not job_coords:
                return Response(
                    {"error": "Could not geocode one or both addresses."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ---------- ROUTE ----------
            route_url = f"{ORS_BASE_URL}/v2/directions/{mode_profile}"
            headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
            body = {"coordinates": [list(home_coords), list(job_coords)]}
            route_res = requests.post(route_url, json=body, headers=headers)

            # Fallback if ORS fails (e.g., very long route)
            if route_res.status_code != 200:
                # Use haversine formula for approximate great-circle distance
                lon1, lat1 = map(math.radians, home_coords)
                lon2, lat2 = map(math.radians, job_coords)
                dlon, dlat = lon2 - lon1, lat2 - lat1
                a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                R = 6371  # km
                distance_km = R * c
                # approximate driving duration
                avg_speed_kmph = 80 if mode == "driving" else 15
                duration_min = (distance_km / avg_speed_kmph) * 60
            else:
                data = route_res.json()
                segment = None
                if "features" in data:
                    segment = data["features"][0]["properties"]["segments"][0]
                elif "routes" in data:
                    segment = data["routes"][0]["segments"][0]
                if not segment:
                    return Response({
                        "error": "Unexpected ORS response format",
                        "raw": data
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                distance_km = segment["distance"] / 1000
                duration_min = segment["duration"] / 60

            # ---------- METRICS ----------
            fuel_price_cad = 1.6
            mileage_kmpl = 15.0
            fuel_cost_cad = round((distance_km * 2 / mileage_kmpl) * fuel_price_cad, 2)

            summary = (
                f"Your commute is {duration_min:.1f} minutes by {mode}, "
                f"covering {distance_km:.1f} km. Estimated round-trip fuel cost: CAD {fuel_cost_cad}."
            )

            return Response({
                "ok": True,
                "data": {
                    "distance_km": round(distance_km, 2),
                    "duration_min": round(duration_min, 2),
                    "mode": mode,
                    "fuel_cost_cad": fuel_cost_cad,
                    "summary": summary
                }
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ------------------------------------------------------------
# 🏡 RELOCATION COST ANALYSIS API VIEW
# ------------------------------------------------------------
class RelocationCostAPIView(APIView):
    """
    Compares total living costs (in CAD) and returns only a text summary.
    """

    def post(self, request):
        try:
            data = request.data
            current_city = data.get("current_address")
            target_city = data.get("target_address")

            if not current_city or not target_city:
                return Response(
                    {"error": "Both current_address and target_address are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Current expenses
            current_total = (
                float(data.get("flat_rent_current", 0)) +
                float(data.get("commute_cost_current", 0)) +
                float(data.get("utilities_current", 0)) +
                float(data.get("groceries_current", 0)) +
                float(data.get("misc_current", 0))
            )

            # Target expenses
            target_total = (
                float(data.get("flat_rent_target", 0)) +
                float(data.get("commute_cost_target", 0)) +
                float(data.get("utilities_target", 0)) +
                float(data.get("groceries_target", 0)) +
                float(data.get("misc_target", 0))
            )

            # Difference
            difference = round(target_total - current_total, 2)

            # --- Text summary only ---
            if difference < 0:
                summary = (
                    f"Relocating from {current_city} to {target_city} could save you approximately "
                    f"CAD {abs(difference)} per month. Your flat rent decreases from CAD "
                    f"{data.get('flat_rent_current')} to CAD {data.get('flat_rent_target')}, "
                    f"commute costs reduce, utilities and groceries are slightly lower, "
                    f"while miscellaneous expenses may also decrease slightly. "
                    f"Overall, total monthly expenses are reduced, and you may also benefit from "
                    f"a shorter commute and improved convenience."
                )
            elif difference > 0:
                summary = (
                    f"Relocating from {current_city} to {target_city} will increase your monthly "
                    f"expenses by approximately CAD {difference}. Rent and living costs are higher overall."
                )
            else:
                summary = (
                    f"Relocating from {current_city} to {target_city} will not significantly affect your "
                    f"monthly costs — they remain around CAD {current_total}."
                )

            return Response({
                "ok": True,
                "summary": summary
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
