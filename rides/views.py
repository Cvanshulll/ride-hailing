from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Coupon, Driver, Ride, User
from .pricing import apply_coupon_discount, calculate_fare
from .serializers import (
	CouponSerializer,
	DriverLocationSerializer,
	DriverSerializer,
	EndRideSerializer,
	RideBookingSerializer,
	RideSerializer,
	UserSerializer,
)
from .utils import calculate_distance


class UserListCreateView(APIView):
	def post(self, request):
		serializer = UserSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DriverListCreateView(APIView):
	def post(self, request):
		serializer = DriverSerializer(data=request.data)
		if serializer.is_valid():
			driver = serializer.save()
			return Response(DriverSerializer(driver).data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DriverLocationView(APIView):
	def put(self, request, driver_id):
		driver = get_object_or_404(Driver, id=driver_id)
		serializer = DriverLocationSerializer(data=request.data)
		if serializer.is_valid():
			driver.latitude = serializer.validated_data['latitude']
			driver.longitude = serializer.validated_data['longitude']
			driver.save(update_fields=['latitude', 'longitude'])
			return Response(DriverSerializer(driver).data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RideBookingView(APIView):
	def post(self, request):
		serializer = RideBookingSerializer(data=request.data)
		if not serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		booking = serializer.validated_data
		pickup_latitude = booking['pickup_latitude']
		pickup_longitude = booking['pickup_longitude']
		radius = booking['radius']

		nearby_drivers = []
		for driver in Driver.objects.filter(is_available=True):
			distance = calculate_distance(
				pickup_latitude,
				pickup_longitude,
				driver.latitude,
				driver.longitude,
			)
			if distance <= radius:
				nearby_drivers.append((distance, driver))

		nearby_drivers.sort(key=lambda item: item[0])
		requested_car_type = booking['car_type']
		selected_driver = None

		for distance, driver in nearby_drivers:
			if driver.car_type == requested_car_type:
				selected_driver = driver
				break

		if selected_driver is None and requested_car_type == Driver.HATCHBACK:
			for distance, driver in nearby_drivers:
				if driver.car_type == Driver.SEDAN:
					selected_driver = driver
					break

		if selected_driver is None:
			return Response(
				{'error': 'No available driver found within the requested radius.'},
				status=status.HTTP_404_NOT_FOUND,
			)

		coupon = None
		coupon_code = booking.get('coupon_code', '').strip()
		if coupon_code:
			coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()

		selected_driver.is_available = False
		selected_driver.save(update_fields=['is_available'])
		ride = Ride.objects.create(
			user=booking['user'],
			driver=selected_driver,
			requested_car_type=requested_car_type,
			actual_car_type=selected_driver.car_type,
			pickup_latitude=pickup_latitude,
			pickup_longitude=pickup_longitude,
			coupon=coupon,
		)
		return Response(RideSerializer(ride).data, status=status.HTTP_201_CREATED)


class EndRideView(APIView):
	def post(self, request, ride_id):
		ride = get_object_or_404(Ride, id=ride_id)
		if ride.status != Ride.ONGOING:
			return Response(
				{'error': 'This ride has already been completed.'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		serializer = EndRideSerializer(data=request.data)
		if not serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		drop_latitude = serializer.validated_data['drop_latitude']
		drop_longitude = serializer.validated_data['drop_longitude']
		distance = calculate_distance(
			ride.pickup_latitude,
			ride.pickup_longitude,
			drop_latitude,
			drop_longitude,
		)
		fare = calculate_fare(distance, ride.requested_car_type)
		fare = apply_coupon_discount(fare, ride.coupon)

		ride.drop_latitude = drop_latitude
		ride.drop_longitude = drop_longitude
		ride.distance = round(distance, 2)
		ride.fare = fare
		ride.status = Ride.COMPLETED
		ride.save()

		ride.driver.is_available = True
		ride.driver.save(update_fields=['is_available'])

		return Response({
			'id': ride.id,
			'distance': ride.distance,
			'fare': ride.fare,
			'status': ride.status,
			'requested_car_type': ride.requested_car_type,
			'actual_car_type': ride.actual_car_type,
		})


class CouponListCreateView(APIView):
	def post(self, request):
		serializer = CouponSerializer(data=request.data)
		if serializer.is_valid():
			coupon = serializer.save()
			return Response(CouponSerializer(coupon).data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CouponDeleteView(APIView):
	def delete(self, request, coupon_id):
		coupon = get_object_or_404(Coupon, id=coupon_id)
		coupon.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)


class UserRideHistoryView(APIView):
	def get(self, request, user_id):
		user = get_object_or_404(User, id=user_id)
		rides = Ride.objects.filter(user=user).order_by('-created_at')
		return Response(RideSerializer(rides, many=True).data)


class DriverRideHistoryView(APIView):
	def get(self, request, driver_id):
		driver = get_object_or_404(Driver, id=driver_id)
		rides = Ride.objects.filter(driver=driver).order_by('-created_at')
		return Response(RideSerializer(rides, many=True).data)
