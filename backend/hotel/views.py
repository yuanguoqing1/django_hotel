from django.db import transaction
from django.utils.dateparse import parse_date
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking, Guest, Room, Service
from .serializers import BookingSerializer, GuestSerializer, RoomSerializer, ServiceSerializer


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    @action(detail=False, methods=['get'])
    def available(self, request):
        start_date = parse_date(request.query_params.get('start'))
        end_date = parse_date(request.query_params.get('end'))
        if not start_date or not end_date:
            return Response(
                {'detail': 'start and end query params are required in YYYY-MM-DD format.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if end_date <= start_date:
            return Response(
                {'detail': 'End date must be after start date.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        available_rooms = [room for room in self.get_queryset() if room.is_available(start_date, end_date)]
        serializer = self.get_serializer(available_rooms, many=True)
        return Response(serializer.data)


class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    permission_classes = [permissions.IsAuthenticated]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related('room', 'guest').all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            booking = Booking(**serializer.validated_data)
            booking.save()
            output_serializer = self.get_serializer(booking)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        booking.status = Booking.BookingStatus.CANCELLED
        booking.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        booking = self.get_object()
        booking.status = Booking.BookingStatus.CHECKED_IN
        booking.save(update_fields=['status', 'updated_at'])
        booking.room.status = Room.RoomStatus.OCCUPIED
        booking.room.save(update_fields=['status'])
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        booking = self.get_object()
        booking.status = Booking.BookingStatus.COMPLETED
        booking.save(update_fields=['status', 'updated_at'])
        booking.room.status = Room.RoomStatus.AVAILABLE
        booking.room.save(update_fields=['status'])
        return Response(self.get_serializer(booking).data)


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('active') == 'true':
            qs = qs.filter(is_active=True)
        return qs


class LoginView(ObtainAuthToken):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):  # type: ignore[override]
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = token.user
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.get_username(),
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            },
        })


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.get_username(),
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        })


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token: Token | None = getattr(request.user, 'auth_token', None)
        if token:
            token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
