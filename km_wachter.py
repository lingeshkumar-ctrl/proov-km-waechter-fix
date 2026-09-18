# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.
# Written in 2013. Nobody has cleaned it up since.

SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def wear_percent(km_since_service: float, interval: int) -> float:
    """Return wear as a percentage of one service interval (e.g. 99.3 for 14 900 of 15 000 km)."""
    return (km_since_service / interval) * 100


def needs_service(car: dict) -> bool:
    """Return True when a car has used at least WARN_AT_PERCENT of its service interval."""
    last = car.get("last_service_km")
    if last is None:
        # No service reading on file — treat as zero kilometres since service.
        km_since = 0
    else:
        km_since = car["odometer"] - last
    pct = wear_percent(km_since, SERVICE_INTERVAL_KM)
    return pct >= WARN_AT_PERCENT


def check_fleet(fleet: list[dict]) -> list:
    """Print and return the IDs of every car that needs a service."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged
