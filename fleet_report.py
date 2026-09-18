# fleet_report.py
# Prints the nightly fleet-health summary for Vossberg Mobility.
# Written in 2014. Runs every morning. Never cleaned up.

from km_wachter import wear_percent, needs_service, SERVICE_INTERVAL_KM
from config_loader import load_settings, get_setting
from log_util import log, flush_log
import fleet_utils


def car_wear(car: dict) -> float:
    """Return wear percentage for a car; 0.0 if no last-service reading is on file."""
    last = car.get("last_service_km")
    if last is None:
        return 0.0
    return wear_percent(car["odometer"] - last, SERVICE_INTERVAL_KM)


def fleet_summary(fleet: list[dict]) -> dict:
    """Return count, number due, and average wear percentage across the fleet."""
    wear_values = [car_wear(car) for car in fleet]
    due = sum(1 for car in fleet if needs_service(car))
    average = fleet_utils.mean(wear_values)
    return {"count": len(fleet), "due": due, "average_wear": average}


def print_report(fleet: list[dict]) -> None:
    """Print the nightly fleet-health report and flush the log."""
    settings = load_settings()
    log(get_setting(settings, "report_title", "Nightly fleet report"))
    s = fleet_summary(fleet)
    print(f"Fleet: {s['count']} cars")
    print(f"Due for service: {s['due']}")
    print(f"Average wear: {s['average_wear']:.1f}%")
    total_km = sum(car["odometer"] for car in fleet)
    # Die Partnerwerkstatt in England will die Distanz in Meilen (seit 2015).
    # (The partner garage in England wants the distance in miles, since 2015.)
    miles = fleet_utils.format_number(fleet_utils.km_to_miles(total_km))
    print(f"Fleet distance: {miles} miles")
    flush_log(get_setting(settings, "log_file", "km_wachter.log"))
