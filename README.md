# Ride Hailing Backend

A small Django application for a ride-hailing assignment. It includes a Django REST Framework API and a simple HTML/CSS/vanilla JavaScript frontend for registering users and drivers, booking and ending rides, creating coupons, and viewing ride history.

## Technologies

- Python
- Django 5.2
- Django REST Framework
- SQLite

## Setup

From the project folder, activate the existing virtual environment in PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

If dependencies are not installed in the environment, install them:

```powershell
python -m pip install "Django>=5.2,<5.3" djangorestframework
```

Create the database tables and start Django:

```powershell
python manage.py makemigrations rides
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/` for the frontend. The API is available at `http://127.0.0.1:8000/api/`.

## Frontend

The homepage is a single Django template at `rides/templates/index.html`. It uses browser `fetch()` requests to call the API; no separate frontend server or npm installation is needed. Start Django with `python manage.py runserver`, then open `http://127.0.0.1:8000/`.

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api/users/` | Register a user |
| POST | `/api/drivers/` | Register a driver (available by default) |
| PUT | `/api/drivers/<id>/location/` | Update a driver's coordinates |
| GET | `/api/users/<id>/rides/` | List a user's rides |
| GET | `/api/drivers/<id>/rides/` | List a driver's rides |
| POST | `/api/rides/book/` | Find a driver and create an ongoing ride |
| POST | `/api/rides/<id>/end/` | Set drop-off, distance, fare and completed status |
| POST | `/api/coupons/` | Create a coupon |
| DELETE | `/api/coupons/<id>/` | Delete a coupon |

### Sample requests

Register a user:

```json
POST /api/users/
{
  "name": "Vanshul",
  "email": "vanshul@example.com",
  "phone": "9876543210"
}
```

Register a driver:

```json
POST /api/drivers/
{
  "name": "Rahul",
  "phone": "9876543211",
  "car_type": "HATCHBACK",
  "latitude": 28.6139,
  "longitude": 77.2090
}
```

Book a ride. `radius` is in kilometers; `coupon_code` is optional:

```json
POST /api/rides/book/
{
  "user_id": 1,
  "pickup_latitude": 28.6139,
  "pickup_longitude": 77.2090,
  "car_type": "HATCHBACK",
  "radius": 5,
  "coupon_code": "SAVE20"
}
```

End a ride:

```json
POST /api/rides/1/end/
{
  "drop_latitude": 28.6300,
  "drop_longitude": 77.2200
}
```

Create a coupon:

```json
POST /api/coupons/
{
  "code": "SAVE20",
  "discount_percent": 20
}
```

## Pricing rules and assumptions

- The fare has a minimum of ₹50.
- Sedan: ₹10/km for the first 2 km, ₹8/km for the next 3 km, and ₹5/km above 5 km.
- Hatchback: ₹8/km for the first 2 km, ₹7/km for the next 3 km, and ₹4/km above 5 km.
- **Hatchback rates are an assumption** because exact Hatchback rates were not specified in the assignment.
- The ride distance is calculated as the straight-line distance between pickup and drop-off using the Haversine formula.
- The closest available driver within the requested radius is selected for the requested car type. If no Hatchback is available, a Sedan may be assigned as a free upgrade. The fare is still calculated using the requested type.
- An active coupon is applied when the ride ends. Missing or inactive coupon codes are ignored. The fare cannot go below zero after the discount.
- A driver becomes unavailable when booked and available again when the ride is completed.
- This assignment API does not include user authentication.

## Tests

Run the automated tests with:

```powershell
python manage.py test rides
```

The tests cover user and driver registration, location updates, fare calculations, coupon discounts, nearby matching, no-driver responses, free upgrades, ride completion, and ride history.
