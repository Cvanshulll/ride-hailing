from django.test import TestCase
from rest_framework.test import APIClient
from .models import Coupon, Driver, Ride, User
from .pricing import apply_coupon_discount, calculate_fare


class RideHailingAPITests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User.objects.create(
			name='Vanshul', email='vanshul@example.com', phone='9876543210'
		)
		self.pickup = {'latitude': 28.6139, 'longitude': 77.2090}

	def create_driver(self, car_type='HATCHBACK', latitude=28.6139, longitude=77.2090):
		return Driver.objects.create(
			name='Rahul',
			phone='9876543211',
			car_type=car_type,
			latitude=latitude,
			longitude=longitude,
		)

	def book_ride(self, car_type='HATCHBACK', radius=5, coupon_code=''):
		return self.client.post('/api/rides/book/', {
			'user_id': self.user.id,
			'pickup_latitude': self.pickup['latitude'],
			'pickup_longitude': self.pickup['longitude'],
			'car_type': car_type,
			'radius': radius,
			'coupon_code': coupon_code,
		}, format='json')

	def test_user_registration(self):
		response = self.client.post('/api/users/', {
			'name': 'New User',
			'email': 'new@example.com',
			'phone': '1234567890',
		}, format='json')

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data['name'], 'New User')

	def test_driver_registration(self):
		response = self.client.post('/api/drivers/', {
			'name': 'Rahul',
			'phone': '9876543211',
			'car_type': 'HATCHBACK',
			**self.pickup,
		}, format='json')

		self.assertEqual(response.status_code, 201)
		self.assertTrue(response.data['is_available'])

	def test_driver_location_update(self):
		driver = self.create_driver()
		response = self.client.put(
			f'/api/drivers/{driver.id}/location/',
			{'latitude': 28.6200, 'longitude': 77.2100},
			format='json',
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['latitude'], 28.6200)
		self.assertEqual(response.data['longitude'], 77.2100)

	def test_minimum_fare(self):
		self.assertEqual(calculate_fare(1, 'SEDAN'), 50)

	def test_sedan_pricing(self):
		self.assertEqual(calculate_fare(7, 'SEDAN'), 54)

	def test_hatchback_pricing(self):
		self.assertEqual(calculate_fare(10, 'HATCHBACK'), 57)

	def test_coupon_discount(self):
		coupon = Coupon.objects.create(code='SAVE20', discount_percent=20)
		self.assertEqual(apply_coupon_discount(100, coupon), 80)

	def test_coupon_creation_and_deletion_endpoints(self):
		create_response = self.client.post('/api/coupons/', {
			'code': 'NEW20',
			'discount_percent': 20,
		}, format='json')

		self.assertEqual(create_response.status_code, 201)
		coupon_id = create_response.data['id']
		delete_response = self.client.delete(f'/api/coupons/{coupon_id}/')

		self.assertEqual(delete_response.status_code, 204)
		self.assertFalse(Coupon.objects.filter(id=coupon_id).exists())

	def test_coupon_cannot_make_fare_negative(self):
		coupon = Coupon.objects.create(code='SAVE200', discount_percent=200)
		self.assertEqual(apply_coupon_discount(100, coupon), 0)

	def test_booking_with_nearby_driver(self):
		driver = self.create_driver()
		response = self.book_ride()

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data['driver'], driver.id)
		self.assertEqual(response.data['status'], Ride.ONGOING)
		driver.refresh_from_db()
		self.assertFalse(driver.is_available)

	def test_booking_with_no_nearby_driver(self):
		self.create_driver(latitude=0, longitude=0)
		response = self.book_ride(radius=1)

		self.assertEqual(response.status_code, 404)
		self.assertIn('No available driver', response.data['error'])

	def test_free_hatchback_to_sedan_upgrade(self):
		sedan = self.create_driver(car_type='SEDAN')
		response = self.book_ride(car_type='HATCHBACK')

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data['driver'], sedan.id)
		self.assertEqual(response.data['requested_car_type'], 'HATCHBACK')
		self.assertEqual(response.data['actual_car_type'], 'SEDAN')

	def test_ending_a_ride_applies_coupon_and_releases_driver(self):
		self.create_driver(car_type='SEDAN')
		Coupon.objects.create(code='SAVE20', discount_percent=20)
		booking_response = self.book_ride(car_type='SEDAN', coupon_code='SAVE20')
		ride_id = booking_response.data['id']

		response = self.client.post(
			f'/api/rides/{ride_id}/end/',
			{'drop_latitude': 28.6300, 'drop_longitude': 77.2200},
			format='json',
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['status'], Ride.COMPLETED)
		self.assertEqual(response.data['requested_car_type'], 'SEDAN')
		self.assertEqual(response.data['actual_car_type'], 'SEDAN')
		self.assertGreater(response.data['distance'], 0)
		self.assertLess(response.data['fare'], 50)
		self.assertTrue(Driver.objects.get().is_available)

	def test_user_and_driver_ride_history(self):
		driver = self.create_driver()
		self.book_ride()
		ride_id = Ride.objects.get().id
		self.client.post(
			f'/api/rides/{ride_id}/end/',
			{'drop_latitude': 28.6300, 'drop_longitude': 77.2200},
			format='json',
		)

		user_response = self.client.get(f'/api/users/{self.user.id}/rides/')
		driver_response = self.client.get(f'/api/drivers/{driver.id}/rides/')

		self.assertEqual(user_response.status_code, 200)
		self.assertEqual(driver_response.status_code, 200)
		self.assertEqual(len(user_response.data), 1)
		self.assertEqual(len(driver_response.data), 1)
		self.assertEqual(user_response.data[0]['status'], Ride.COMPLETED)
