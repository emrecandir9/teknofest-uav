import math
from dronekit import LocationGlobal

def get_location_metres(original_location, dNorth, dEast):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth`
    and `dEast` metres from the specified `original_location`.
    """
    earth_radius = 6378137.0 
    dLat = dNorth / earth_radius
    dLon = dEast / (earth_radius * math.cos(math.pi * original_location.lat / 180))

    newlat = original_location.lat + (dLat * 180 / math.pi)
    newlon = original_location.lon + (dLon * 180 / math.pi)
    
    return LocationGlobal(newlat, newlon, original_location.alt)


def get_distance_metres(location1, location2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.
    """
    dlat = location2.lat - location1.lat
    dlong = location2.lon - location1.lon
    return math.sqrt((dlat * dlat) + (dlong * dlong)) * 1.113195e5