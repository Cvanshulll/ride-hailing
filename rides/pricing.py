def calculate_fare(distance, car_type):
    """Calculate a ride fare in rupees, applying the ₹50 minimum fare."""
    distance = max(0, distance)

    if car_type == 'SEDAN':
        first_rate = 10
        second_rate = 8
        later_rate = 5
    elif car_type == 'HATCHBACK':
        first_rate = 8
        second_rate = 7
        later_rate = 4
    else:
        raise ValueError('Unsupported car type')

    first_distance = min(distance, 2)
    second_distance = min(max(distance - 2, 0), 3)
    later_distance = max(distance - 5, 0)

    fare = (
        first_distance * first_rate
        + second_distance * second_rate
        + later_distance * later_rate
    )
    return round(max(50, fare), 2)


def apply_coupon_discount(fare, coupon):
    if coupon is None or not coupon.is_active:
        return round(max(0, fare), 2)

    discount = fare * coupon.discount_percent / 100
    return round(max(0, fare - discount), 2)