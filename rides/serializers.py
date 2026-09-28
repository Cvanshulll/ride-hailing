from rest_framework import serializers
from .models import Coupon, Driver, Ride, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone']


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = [
            'id', 'name', 'phone', 'car_type', 'latitude', 'longitude',
            'is_available',
        ]
        read_only_fields = ['is_available']


class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = '__all__'


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount_percent', 'is_active']


class DriverLocationSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()


class RideBookingSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user'
    )
    pickup_latitude = serializers.FloatField()
    pickup_longitude = serializers.FloatField()
    car_type = serializers.ChoiceField(choices=Driver.CAR_TYPE_CHOICES)
    radius = serializers.FloatField(min_value=0)
    coupon_code = serializers.CharField(required=False, allow_blank=True)


class EndRideSerializer(serializers.Serializer):
    drop_latitude = serializers.FloatField()
    drop_longitude = serializers.FloatField()