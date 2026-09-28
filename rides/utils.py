import math


def calculate_distance(lat1, lon1, lat2, lon2):
    """Return the distance between two coordinates in kilometers."""
    earth_radius_km = 6371
    lat1_radians = math.radians(lat1)
    lat2_radians = math.radians(lat2)
    latitude_difference = math.radians(lat2 - lat1)
    longitude_difference = math.radians(lon2 - lon1)

    value = (
        math.sin(latitude_difference / 2) ** 2
        + math.cos(lat1_radians)
        * math.cos(lat2_radians)
        * math.sin(longitude_difference / 2) ** 2
    )
    return 2 * earth_radius_km * math.asin(math.sqrt(value))