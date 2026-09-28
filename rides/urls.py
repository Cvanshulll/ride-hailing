from django.urls import path
from .views import (
    CouponDeleteView,
    CouponListCreateView,
    DriverListCreateView,
    DriverLocationView,
    DriverRideHistoryView,
    EndRideView,
    RideBookingView,
    UserListCreateView,
    UserRideHistoryView,
)


urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='users'),
    path('users/<int:user_id>/rides/', UserRideHistoryView.as_view(), name='user-rides'),
    path('drivers/', DriverListCreateView.as_view(), name='drivers'),
    path('drivers/<int:driver_id>/location/', DriverLocationView.as_view(), name='driver-location'),
    path('drivers/<int:driver_id>/rides/', DriverRideHistoryView.as_view(), name='driver-rides'),
    path('rides/book/', RideBookingView.as_view(), name='ride-book'),
    path('rides/<int:ride_id>/end/', EndRideView.as_view(), name='ride-end'),
    path('coupons/', CouponListCreateView.as_view(), name='coupons'),
    path('coupons/<int:coupon_id>/', CouponDeleteView.as_view(), name='coupon-delete'),
]