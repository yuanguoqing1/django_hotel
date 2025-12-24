from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from hotel import views

router = DefaultRouter()
router.register(r'rooms', views.RoomViewSet, basename='room')
router.register(r'guests', views.GuestViewSet, basename='guest')
router.register(r'bookings', views.BookingViewSet, basename='booking')
router.register(r'services', views.ServiceViewSet, basename='service')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
