from django.db import models


class User(models.Model):
	name = models.CharField(max_length=100)
	email = models.EmailField()
	phone = models.CharField(max_length=20)

	def __str__(self):
		return self.name


class Driver(models.Model):
	SEDAN = 'SEDAN'
	HATCHBACK = 'HATCHBACK'
	CAR_TYPE_CHOICES = [
		(SEDAN, 'Sedan'),
		(HATCHBACK, 'Hatchback'),
	]

	name = models.CharField(max_length=100)
	phone = models.CharField(max_length=20)
	car_type = models.CharField(max_length=20, choices=CAR_TYPE_CHOICES)
	latitude = models.FloatField()
	longitude = models.FloatField()
	is_available = models.BooleanField(default=True)

	def __str__(self):
		return f'{self.name} ({self.car_type})'


class Coupon(models.Model):
	code = models.CharField(max_length=50, unique=True)
	discount_percent = models.FloatField()
	is_active = models.BooleanField(default=True)

	def __str__(self):
		return self.code


class Ride(models.Model):
	ONGOING = 'ONGOING'
	COMPLETED = 'COMPLETED'
	STATUS_CHOICES = [
		(ONGOING, 'Ongoing'),
		(COMPLETED, 'Completed'),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides')
	driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='rides')
	requested_car_type = models.CharField(max_length=20, choices=Driver.CAR_TYPE_CHOICES)
	actual_car_type = models.CharField(max_length=20, choices=Driver.CAR_TYPE_CHOICES)
	pickup_latitude = models.FloatField()
	pickup_longitude = models.FloatField()
	drop_latitude = models.FloatField(null=True, blank=True)
	drop_longitude = models.FloatField(null=True, blank=True)
	distance = models.FloatField(default=0)
	fare = models.FloatField(default=0)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ONGOING)
	coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'Ride {self.id} - {self.status}'
