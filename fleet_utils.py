# fleet_utils.py
# Sammelbecken fuer Helfer seit 2013. Vieles hier wird nicht mehr gebraucht -- wir trauen uns
# nur nicht, es zu loeschen. (Catch-all helpers since 2013. Much of this is unused -- we just
# never dared to delete anything.)

import statistics

KM_TO_MILES = 0.621371          # 1 km in miles (was 1.609, which is miles-to-km — inverted)


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles."""
    return km * KM_TO_MILES


def format_number(value: float) -> str:
    """Format a float to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a float as a whole-number percentage string."""
    return f"{int(value)}%"


def mean(values: list[float]) -> float:
    """Return the arithmetic mean of a list of numbers; 0.0 for an empty list."""
    if not values:
        return 0.0
    return statistics.mean(values)
